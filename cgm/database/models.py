from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func

from cgm.constants import SRID

Base = declarative_base()


class RPG(Base):
    __tablename__ = 'rpg'
    id_parcel = Column("id_parcel", Integer, primary_key=True, index=True)
    code_cultu = Column("code_cultu", String)
    geometry = Column("geometry", Geometry("POLYGON", srid=SRID))
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
