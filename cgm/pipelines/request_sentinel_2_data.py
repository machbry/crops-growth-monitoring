from datetime import datetime
from typing import List
from uuid import uuid4

from geoalchemy2.shape import to_shape
from pystac_client import Client
from shapely.geometry import MultiPolygon

from cgm.logger import get_logger
from cgm.database.requests import get_all_rpg_parcels
from cgm.constants import CATALOGS_FOLDER, SERVER_TIMEZONE
from cgm.database.models import CatalogQuery, ParcelQuery, Parcel
from cgm.database.session import get_session

log = get_logger()


def request_sentinel_2_data(parcels_to_requests: List[Parcel], from_datetime, to_datetime, collection="sentinel-2-l2a"):
    # Init
    query_started_at = datetime.now(tz=SERVER_TIMEZONE)

    # Create catalog
    catalog = Client.open("https://earth-search.aws.element84.com/v1/")

    # Make geometry with all parcels
    geometry_for_sentinel_2_query = MultiPolygon([to_shape(parcel.geometry) for parcel in get_all_rpg_parcels()])

    # Prepare the query
    query = catalog.search(collections=[collection],
                           datetime=[from_datetime, to_datetime],
                           limit=100,
                           intersects=geometry_for_sentinel_2_query)

    log.info("Catalog query prepared : collection %s from %s to %s for the %s parcels", collection, from_datetime,
             to_datetime, len(parcels_to_requests))

    # Do the query
    items = query.item_collection()

    # uuid for this request
    catalog_query_uuid = str(uuid4())

    log.info("%s items collected for the query %s", len(items), catalog_query_uuid)

    # Save results in a json file
    json_name = f"{collection}_{from_datetime.strftime('%Y-%m-%d')}_to_{to_datetime.strftime('%Y-%m-%d')}_{catalog_query_uuid}.json"
    item_collection_json_path = CATALOGS_FOLDER / json_name
    query.item_collection().save_object(item_collection_json_path)

    log.info("item collection saved into json file %s", item_collection_json_path)

    # Log request in database
    stac_request = CatalogQuery(uuid=catalog_query_uuid,
                                collection=collection,
                                from_datetime=from_datetime,
                                to_datetime=to_datetime,
                                nb_items_retrieved=len(items),
                                item_collection_json=str(item_collection_json_path),
                                started_at=query_started_at,
                                done_at=datetime.now(tz=SERVER_TIMEZONE))

    parcels_ids_requested = [parcel.id for parcel in parcels_to_requests]

    parcels_queries = [ParcelQuery(parcel_id_fk=id_parcel,
                                   catalog_query_uuid_fk=catalog_query_uuid) for id_parcel in
                       parcels_ids_requested]

    with get_session() as session:
        session.add(stac_request)
        session.add_all(parcels_queries)
        session.commit()
