"""add weight and price_per_100g fields to price_submissions

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-07 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('price_submissions', sa.Column('weight_value', sa.Float(), nullable=True))
    op.add_column('price_submissions', sa.Column('weight_unit', sa.String(), nullable=True))
    op.add_column('price_submissions', sa.Column('price_per_100g', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('price_submissions', 'price_per_100g')
    op.drop_column('price_submissions', 'weight_unit')
    op.drop_column('price_submissions', 'weight_value')
