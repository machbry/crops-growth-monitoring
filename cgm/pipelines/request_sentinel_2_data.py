from uuid import uuid4

from geoalchemy2.shape import to_shape
from pystac_client import Client
from shapely.geometry import MultiPolygon

from cgm.logger import get_logger
from cgm.database.requests import get_all_rpg_parcels
from cgm.constants import DATA_FOLDER
from cgm.database.models import STACRequest, RPGRequest
from cgm.database.session import get_session

log = get_logger()


def request_sentinel_2_data(datetime_min, datetime_max, collection="sentinel-2-l2a"):
    # Get parcels for which we want to request data from collection
    # TODO : create groups of parcels that are close / contiguous and separate api requests for each one
    parcels_to_requests = get_all_rpg_parcels()

    log.info("%s parcels uploaded from database", len(parcels_to_requests))

    # Create catalog
    catalog = Client.open("https://earth-search.aws.element84.com/v1/")

    # Make geometry with all parcels
    geometry_for_sentinel_2_query = MultiPolygon([to_shape(parcel.geometry) for parcel in get_all_rpg_parcels()])

    # Prepare the query
    query = catalog.search(collections=[collection],
                           datetime=[datetime_min, datetime_max],
                           limit=100,
                           intersects=geometry_for_sentinel_2_query)

    log.info("STAC query prepared : collection %s from %s to %s for the %s parcels", collection, datetime_min,
             datetime_max, len(parcels_to_requests))

    # Do the query
    items = query.item_collection()

    # uuid for this request
    stac_request_uuid = str(uuid4())

    log.info("%s items collected for the query %s", len(items), stac_request_uuid)

    # Save results in a json file
    json_name = f"{collection}_{datetime_min.strftime('%Y-%m-%d')}_to_{datetime_max.strftime('%Y-%m-%d')}_{stac_request_uuid}.json"
    item_collection_json_path = DATA_FOLDER / json_name
    query.item_collection().save_object(item_collection_json_path)

    log.info("item collection saved into json file %s", item_collection_json_path)

    # Log request in database
    stac_request = STACRequest(uuid=stac_request_uuid,
                               collection=collection,
                               datetime_min=datetime_min,
                               datetime_max=datetime_max,
                               nb_items_retrieved=len(items),
                               item_collection_json=str(item_collection_json_path))

    parcels_ids_requested = [parcel.id_parcel for parcel in parcels_to_requests]

    rpg_requests = [RPGRequest(stac_request_id=stac_request_uuid, rpg_id=id_parcel) for id_parcel in
                    parcels_ids_requested]

    with get_session() as session:
        session.add(stac_request)
        session.add_all(rpg_requests)
        session.commit()
