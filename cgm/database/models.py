from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Uuid
from sqlalchemy.orm import relationship

from cgm.constants import SRID

Base = declarative_base()


class RPG(Base):
    __tablename__ = 'rpg'
    id_parcel = Column("id_parcel", Integer, primary_key=True, index=True)
    code_cultu = Column("code_cultu", String)
    geometry = Column("geometry", Geometry("POLYGON", srid=SRID))
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", DateTime(timezone=True), onupdate=func.now())

    rpg_requests = relationship("RPGRequest", back_populates="rpg", cascade="all, delete")


class STACRequest(Base):
    __tablename__ = 'stac_requests'
    uuid = Column("uuid", Uuid, primary_key=True, index=True)
    collection = Column("collection", String)
    datetime_min = Column("datetime_min", DateTime(timezone=True), server_default=func.now())
    datetime_max = Column("datetime_max", DateTime(timezone=True), server_default=func.now())
    nb_items_retrieved = Column("nb_items_retrieved", Integer)
    item_collection_json = Column("item_collection_json", String)

    rpg_requests = relationship("RPGRequest", back_populates="stac_request", cascade="all, delete")


class RPGRequest(Base):
    __tablename__ = 'rpg_requests'
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    stac_request_id = Column(Uuid, ForeignKey('stac_requests.uuid', ondelete="CASCADE"), nullable=False)
    rpg_id = Column(Integer, ForeignKey('rpg.id_parcel', ondelete="CASCADE"), nullable=False)

    stac_request = relationship("STACRequest", back_populates="rpg_requests")
    rpg = relationship("RPG", back_populates="rpg_requests")
