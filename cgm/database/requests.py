from typing import List, Tuple
from uuid import UUID

from sqlalchemy import select, func

from cgm.database.models import Parcel, ParcelQuery, CatalogQuery
from cgm.database.session import get_session


def get_all_rpg_parcels() -> List[Parcel]:
    with get_session() as session:
        query = select(Parcel)
        results = session.execute(query).scalars().all()

    return results


def get_pending_parcels_for_index_computation_by_catalog_query() -> List[Tuple[UUID, List[int]]]:
    with get_session() as session:
        query = select(ParcelQuery.catalog_query_uuid_fk,
                       func.array_agg(ParcelQuery.parcel_id_fk)
                       ).filter(ParcelQuery.index_computed_at == None
        ).group_by(ParcelQuery.catalog_query_uuid_fk)

        results = session.execute(query).all()

    return results


def get_catalog_query_by_uuid(catalog_query: UUID) -> CatalogQuery:
    with get_session() as session:
        query = select(CatalogQuery).filter(CatalogQuery.uuid == catalog_query)
        result = session.execute(query).scalar()

    return result


def get_parcel_by_id(parcel_id: int) -> Parcel:
    with get_session() as session:
        query = select(Parcel).filter(Parcel.id == parcel_id)
        result = session.execute(query).scalar()

    return result
