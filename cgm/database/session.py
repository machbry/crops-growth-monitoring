from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cgm.constants import CGM_POSTGRES_DB_URL

engine = None


def init_engine():
    global engine
    engine = create_engine(CGM_POSTGRES_DB_URL, echo=False)


def get_session():
    if not engine:
        init_engine()

    return sessionmaker(bind=engine)()
