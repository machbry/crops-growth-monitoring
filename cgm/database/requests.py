from typing import List

from sqlalchemy import select

from cgm.database.models import RPG
from cgm.database.session import get_session


def get_all_rpg_parcels() -> List[RPG]:
    with get_session() as session:
        query = select(RPG)
        results = session.execute(query).scalars().all()

    return results
