"""Create table for parcels index

Revision ID: cb3108b7e5d3
Revises: 7ec9b5033fe3
Create Date: 2024-07-22 19:09:47.279864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb3108b7e5d3'
down_revision: Union[str, None] = '7ec9b5033fe3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('parcels_queries', sa.Column('index_computed_at', sa.DateTime(timezone=True), nullable=True))

    op.create_table('parcels_index',
        sa.Column('parcel_id_fk', sa.Integer(), sa.ForeignKey('parcels.id', ondelete="CASCADE"),
                  nullable=False, primary_key=True, index=True),
        sa.Column('datetime', sa.DateTime(timezone=True), primary_key=True, index=True, nullable=False),
        sa.Column('mean_ndvi', sa.Float(), nullable=False),
        sa.Column('mean_ndmi', sa.Float(), nullable=False),
        sa.Column('ndvi_cog_file', sa.String(), nullable=False),
        sa.Column('ndmi_cog_file', sa.String(), nullable=False),
        sa.Column("resolution", sa.Float),
        sa.Column("usable_data_size", sa.Integer),
        sa.ForeignKeyConstraint(['parcel_id_fk'], ['parcels.id'], ondelete='CASCADE')
    )


def downgrade():
    op.drop_table('parcels_index')

    op.drop_column('parcels_queries', 'index_computed_at')
