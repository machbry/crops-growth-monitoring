from typing import List

from sqlalchemy import select

from cgm.database.models import Parcel
from cgm.database.session import get_session


def get_all_rpg_parcels() -> List[Parcel]:
    with get_session() as session:
        query = select(Parcel)
        results = session.execute(query).scalars().all()

    return results
