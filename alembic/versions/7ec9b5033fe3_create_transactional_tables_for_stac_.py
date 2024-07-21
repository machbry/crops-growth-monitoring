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
        'stac_requests',
        sa.Column('uuid', sa.Uuid, primary_key=True, index=True),
        sa.Column('collection', sa.String, nullable=False),
        sa.Column('datetime_min', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('datetime_max', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('nb_items_retrieved', sa.Integer, default=0),
        sa.Column('item_collection_json', sa.String)
    )

    # Create rpg_requests table
    op.create_table(
        'rpg_requests',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('stac_request_id', sa.Uuid,
                  sa.ForeignKey('stac_requests.uuid', ondelete="CASCADE"), nullable=False),
        sa.Column('rpg_id', sa.Integer,
                  sa.ForeignKey('rpg.id_parcel', ondelete="CASCADE"), nullable=False)
    )


def downgrade() -> None:
    # Drop rpg_requests table
    op.drop_table('rpg_requests')

    # Drop stac_requests table
    op.drop_table('stac_requests')
