"""create rpg table

Revision ID: 2ade7287c0aa
Revises: 
Create Date: 2024-07-21 17:49:59.053462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

from cgm.constants import SRID

# revision identifiers, used by Alembic.
revision: str = '2ade7287c0aa'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("parcels",
                    sa.Column("id", sa.Integer, primary_key=True, index=True),
                    sa.Column("code_cultu", sa.String),
                    sa.Column("geometry", Geometry("POLYGON", srid=SRID)),
                    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
                    sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()))


def downgrade() -> None:
    op.drop_table("parcels")
