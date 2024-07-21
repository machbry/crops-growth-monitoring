"""create rpg table

Revision ID: 2ade7287c0aa
Revises: 
Create Date: 2024-07-21 17:49:59.053462

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, Integer, String, DateTime, func
from geoalchemy2 import Geometry

from cgm.constants import SRID

# revision identifiers, used by Alembic.
revision: str = '2ade7287c0aa'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("rpg",
                    Column("id_parcel", Integer, primary_key=True, index=True),
                    Column("code_cultu", String),
                    Column("geometry", Geometry("POLYGON", srid=SRID)),
                    Column("created_at", DateTime(timezone=True), server_default=func.now()),
                    Column("updated_at", DateTime(timezone=True), onupdate=func.now()))


def downgrade() -> None:
    op.drop_table("rpg")
