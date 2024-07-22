"""create transactional tables for stac requests

Revision ID: 7ec9b5033fe3
Revises: 2ade7287c0aa
Create Date: 2024-07-21 22:10:04.213023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ec9b5033fe3'
down_revision: Union[str, None] = '2ade7287c0aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create stac_requests table
    op.create_table(
        'catalog_queries',
        sa.Column('uuid', sa.Uuid, primary_key=True, index=True),
        sa.Column('collection', sa.String, nullable=False),
        sa.Column('datetime_min', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('datetime_max', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('nb_items_retrieved', sa.Integer, default=0),
        sa.Column('item_collection_json', sa.String),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True))
    )

    # Create rpg_requests table
    op.create_table(
        'parcels_queries',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('parcel_id_fk', sa.Integer,
                  sa.ForeignKey('parcels.id', ondelete="CASCADE"), nullable=False),
        sa.Column('catalog_query_uuid_fk', sa.Uuid,
                  sa.ForeignKey('catalog_queries.uuid', ondelete="CASCADE"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('parcels_queries')

    op.drop_table('catalog_queries')
