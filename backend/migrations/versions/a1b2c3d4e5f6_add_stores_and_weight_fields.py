"""add stores table and weight fields

Revision ID: a1b2c3d4e5f6
Revises: ff9bb2740a43
Create Date: 2026-03-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ff9bb2740a43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create stores table
    op.create_table('stores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_stores_id'), 'stores', ['id'], unique=False)

    # Add weight columns to grocery_items
    op.add_column('grocery_items', sa.Column('weight_value', sa.Float(), nullable=True))
    op.add_column('grocery_items', sa.Column('weight_unit', sa.String(), nullable=True))

    # Add store_id column (nullable first for backfill)
    op.add_column('price_submissions', sa.Column('store_id', sa.Integer(), nullable=True))

    # Backfill: create Store records from distinct store_name values
    conn = op.get_bind()
    distinct_stores = conn.execute(
        sa.text("SELECT DISTINCT store_name FROM price_submissions")
    ).fetchall()
    for (store_name,) in distinct_stores:
        conn.execute(
            sa.text("INSERT INTO stores (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
            {"name": store_name},
        )

    # Backfill store_id from store_name
    conn.execute(
        sa.text(
            "UPDATE price_submissions SET store_id = stores.id "
            "FROM stores WHERE price_submissions.store_name = stores.name"
        )
    )

    # Drop store_name column and make store_id non-nullable
    op.drop_column('price_submissions', 'store_name')
    op.alter_column('price_submissions', 'store_id', nullable=False)
    op.create_foreign_key(
        'fk_price_submissions_store_id',
        'price_submissions', 'stores',
        ['store_id'], ['id'],
    )


def downgrade() -> None:
    # Add store_name back
    op.add_column('price_submissions', sa.Column('store_name', sa.String(), nullable=True))

    # Backfill store_name from stores
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE price_submissions SET store_name = stores.name "
            "FROM stores WHERE price_submissions.store_id = stores.id"
        )
    )
    op.alter_column('price_submissions', 'store_name', nullable=False)

    # Drop store_id and FK
    op.drop_constraint('fk_price_submissions_store_id', 'price_submissions', type_='foreignkey')
    op.drop_column('price_submissions', 'store_id')

    # Drop weight columns
    op.drop_column('grocery_items', 'weight_unit')
    op.drop_column('grocery_items', 'weight_value')

    # Drop stores table
    op.drop_index(op.f('ix_stores_id'), table_name='stores')
    op.drop_table('stores')
