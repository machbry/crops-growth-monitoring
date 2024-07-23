import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime

from pystac import ItemCollection
from odc.stac import stac_load
from geoalchemy2.shape import to_shape
from rasterio.features import geometry_mask
from odc.geo.xr import write_cog

from cgm.database.requests import get_pending_parcels_for_index_computation_by_catalog_query, get_catalog_query_by_uuid, get_parcel_by_id, save_parcel_index, update_parcel_query
from cgm.constants import COGS_FOLDER, SERVER_TIMEZONE, SRID
from cgm.database.models import ParcelIndex
from cgm.logger import get_logger

log = get_logger()


# TODO : do async computations and extract computation steps in a dedicated functions
def compute_pending_parcels_index(resolution: float, max_parcels_to_compute: int, compute_all: bool):
    if compute_all:
        log.info("All pending parcels index computations will be done at resolution %s", resolution)
    else:
        log.info("A maximum of %s parcels index will be computed at resolution %s", max_parcels_to_compute, resolution)

    # For pending parcels queries to compute, we get the list of parcels ids grouped by catalog query uuid
    pending_parcels_queries = get_pending_parcels_for_index_computation_by_catalog_query()
    log.info("%s catalog queries have pending parcels index to compute", len(pending_parcels_queries))

    # We stop pipeline run if there is no pending computation
    if len(pending_parcels_queries) == 0:
        log.info("No pending parcels index to compute")
        return

    nb_parcels_computed = 0
    for catalog_query_uuid, parcels_ids in pending_parcels_queries:
        log.info("%s parcels are waiting for compute for the catalog query %s", len(parcels_ids), catalog_query_uuid)

        catalog_query = get_catalog_query_by_uuid(catalog_query_uuid)

        items = ItemCollection.from_file(catalog_query.item_collection_json)

        p = 0
        while (compute_all or nb_parcels_computed < max_parcels_to_compute) and p < len(parcels_ids):

            parcel_id = parcels_ids[p]

            log.info("Start of index computations ; parcel %s ; from %s ; to %s",
                     parcel_id, catalog_query.from_datetime, catalog_query.to_datetime)

            parcel = get_parcel_by_id(parcel_id)
            parcel_shape = to_shape(parcel.geometry)

            # Load stac data from the items collection (without computation)
            data = stac_load(items,
                             bands=["scl", "nir", "red", "swir16"],
                             crs=f"epsg:{SRID}",
                             resolution=resolution,
                             chunks={},
                             groupby="solar_day",
                             geopolygon=parcel_shape)

            log.info("Stac data loaded ; parcel %s ; from %s ; to %s",
                     parcel_id, catalog_query.from_datetime, catalog_query.to_datetime)

            # Filter stac data on the shape of the parcel
            ShapeMask = geometry_mask([parcel_shape],
                                      out_shape=(len(data.latitude), len(data.longitude)),
                                      transform=data.odc.geobox.transform,
                                      invert=True)
            ShapeMask = xr.DataArray(ShapeMask, dims=("latitude", "longitude"))
            data = data.where(ShapeMask == True, drop=True)

            log.info("Stac data filtered on parcel shape ; parcel %s ; from %s ; to %s",
                     parcel_id, catalog_query.from_datetime, catalog_query.to_datetime)

            # Create ndvi and ndmi variables
            data["nir"] = data.nir.astype(int)
            data["red"] = data.red.astype(int)
            data["swir16"] = data.swir16.astype(int)

            data["ndvi"] = (data.nir - data.red) / (data.nir + data.red)
            data["ndmi"] = (data.nir - data.swir16) / (data.nir + data.swir16)

            log.info("NDVI and NDMI index created ; parcel %s ; from %s ; to %s",
                     parcel_id, catalog_query.from_datetime, catalog_query.to_datetime)

            # Compute index
            data = data.compute()
            log.info("Index computed ; parcel %s ; from %s ; to %s)",
                     parcel_id, catalog_query.from_datetime, catalog_query.to_datetime)

            # Filter zones with clouds using SCL classification
            data = data.where(data.scl.isin([4, 5, 6, 7]), drop=True)

            log.info("Zones with clouds filtered from data ; parcel %s ; from %s ; to %s",
                     parcel_id, catalog_query.from_datetime, catalog_query.to_datetime)

            time_values = data['time'].values
            if len(time_values) == 0:
                log.warning("No data left to compute index after filtering clouds ; parcel %s ; from %s ; to %s",
                            parcel_id, catalog_query.from_datetime, catalog_query.to_datetime)

            for t in time_values:

                day = np.datetime_as_string(t, unit='D')
                data_t = data.sel(time=t)

                # Compute mean values for ndvi and ndmi
                ndvi_t = data_t['ndvi']
                mean_ndvi_t = ndvi_t.mean(dim=['latitude', 'longitude'], skipna=True)

                ndmi_t = data_t['ndmi']
                mean_ndmi_t = ndmi_t.mean(dim=['latitude', 'longitude'], skipna=True)

                # Save index results in COG files
                parcel_cogs_folder = COGS_FOLDER / f'{parcel.id}'

                parcel_cogs_ndvi_folder = parcel_cogs_folder / 'ndvi'
                parcel_cogs_ndvi_folder.mkdir(exist_ok=True, parents=True)

                parcel_cogs_nmdi_folder = parcel_cogs_folder / 'nmdi'
                parcel_cogs_nmdi_folder.mkdir(exist_ok=True, parents=True)

                ndvi_cog_file_path = parcel_cogs_ndvi_folder / f'{parcel.id}_ndvi_{day}.tiff'
                write_cog(ndvi_t, fname=ndvi_cog_file_path, overwrite=True)

                log.info("NDVI COG file saved at %s ; parcel %s ; day %s", ndvi_cog_file_path, parcel.id, day)

                ndmi_cog_file_path = parcel_cogs_nmdi_folder / f'{parcel.id}_ndmi_{day}.tiff'
                write_cog(ndmi_t, fname=ndmi_cog_file_path, overwrite=True)

                log.info("NDMI COG file saved at %s ; parcel %s ; day %s", ndmi_cog_file_path, parcel.id, day)

                # Saving index computation results in database
                parcel_index = ParcelIndex(parcel_id=parcel.id,
                                           datetime=pd.to_datetime(t),
                                           mean_ndvi=float(mean_ndvi_t),
                                           mean_ndmi=float(mean_ndmi_t),
                                           ndvi_cog_file=str(ndvi_cog_file_path),
                                           ndmi_cog_file=str(ndmi_cog_file_path),
                                           resolution=resolution,
                                           usable_data_size=data_t.dims["longitude"] * data_t.dims["latitude"])

                save_parcel_index(parcel_index)
                log.info("Index computation results saved in database ; parcel %s ; time %s", parcel.id, t)

            # Log in database that its parcel query has been computed
            update_parcel_query(parcel=parcel,
                                catalog_query=catalog_query,
                                index_computed_at=datetime.now(tz=SERVER_TIMEZONE),
                                resolution=resolution,
                                usable_data_size=data.dims["time"] * data.dims["longitude"] * data.dims["latitude"])

            p += 1
            nb_parcels_computed += 1

            log.info("End of index computations ; parcel %s ; from %s ; to %s", parcel_id, catalog_query.from_datetime,
                     catalog_query.to_datetime)
