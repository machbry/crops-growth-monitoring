from ast import Index

from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Uuid, Float, Boolean
from sqlalchemy.orm import relationship

from cgm.constants import SRID

Base = declarative_base()


class Parcel(Base):
    __tablename__ = 'parcels'
    id = Column("id", Integer, primary_key=True, index=True)
    code_cultu = Column("code_cultu", String)
    geometry = Column("geometry", Geometry("POLYGON", srid=SRID))
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", DateTime(timezone=True), onupdate=func.now())

    parcel_queries = relationship("ParcelQuery", back_populates="parcel", cascade="all, delete")
    parcel_indexes = relationship("ParcelIndex", back_populates="parcel", cascade="all, delete")


class CatalogQuery(Base):
    __tablename__ = 'catalog_queries'
    uuid = Column("uuid", Uuid, primary_key=True, index=True)
    collection = Column("collection", String)
    from_datetime = Column("datetime_min", DateTime(timezone=True))
    to_datetime = Column("datetime_max", DateTime(timezone=True))
    nb_items_retrieved = Column("nb_items_retrieved", Integer)
    item_collection_json = Column("item_collection_json", String)
    started_at = Column("started_at", DateTime(timezone=True))
    done_at = Column("finished_at", DateTime(timezone=True))

    parcel_queries = relationship("ParcelQuery", back_populates="catalog_query", cascade="all, delete")


class ParcelQuery(Base):
    __tablename__ = 'parcels_queries'
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    parcel_id_fk = Column("parcel_id_fk", Integer, ForeignKey('parcels.id', ondelete="CASCADE"), nullable=False)
    catalog_query_uuid_fk = Column("catalog_query_uuid_fk", Uuid, ForeignKey('catalog_queries.uuid', ondelete="CASCADE"), nullable=False)
    index_computed_at = Column("index_computed_at", DateTime(timezone=True), default=None)

    parcel = relationship("Parcel", back_populates="parcel_queries")
    catalog_query = relationship("CatalogQuery", back_populates="parcel_queries")


class ParcelIndex(Base):
    __tablename__ = 'parcels_index'
    parcel_id_fk = Column("parcel_id_fk", Integer, ForeignKey('parcels.id', ondelete="CASCADE"),
                          primary_key=True, index=True, nullable=False)
    datetime = Column("datetime", DateTime(timezone=True), primary_key=True, index=True, nullable=False)
    mean_ndvi = Column("mean_ndvi", Float, nullable=False)
    mean_ndmi = Column("mean_ndmi", Float, nullable=False)
    ndvi_cog_file = Column("ndvi_cog_file", String, nullable=False)
    ndmi_cog_file = Column("ndmi_cog_file", String, nullable=False)

    parcel = relationship("Parcel", back_populates="parcel_indexes")
