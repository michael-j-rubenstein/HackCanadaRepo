"""new schema refactor - simplified product/submission/price tracking

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-03-07 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Drop materialized views first ---
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_category_price_daily")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_product_price_daily")

    # --- Drop old tables in correct order (respecting FKs) ---
    op.drop_table('pinned_items')
    op.drop_table('shopping_cart_items')
    op.drop_table('price_alerts')
    op.drop_table('submission_items')
    op.drop_table('price_submissions')
    op.drop_table('submissions')
    op.drop_table('receipts')
    op.drop_table('grocery_items')
    op.drop_table('categories')
    op.drop_table('stores')
    op.drop_table('users')

    # --- Create new tables ---

    # Categories
    op.create_table('categories',
        sa.Column('c_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('c_id'),
    )
    op.create_index(op.f('ix_categories_c_id'), 'categories', ['c_id'], unique=False)

    # Brands
    op.create_table('brands',
        sa.Column('brand_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('brand_id'),
    )
    op.create_index(op.f('ix_brands_brand_id'), 'brands', ['brand_id'], unique=False)

    # Stores
    op.create_table('stores',
        sa.Column('store_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('store_id'),
    )
    op.create_index(op.f('ix_stores_store_id'), 'stores', ['store_id'], unique=False)

    # Users
    op.create_table('users',
        sa.Column('u_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('u_id'),
    )
    op.create_index(op.f('ix_users_u_id'), 'users', ['u_id'], unique=False)

    # Product Items
    op.create_table('product_items',
        sa.Column('p_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('c_id', sa.String(), nullable=False),
        sa.Column('brand_id', sa.String(), nullable=False),
        sa.Column('store_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['c_id'], ['categories.c_id']),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.brand_id']),
        sa.ForeignKeyConstraint(['store_id'], ['stores.store_id']),
        sa.PrimaryKeyConstraint('p_id'),
    )
    op.create_index(op.f('ix_product_items_p_id'), 'product_items', ['p_id'], unique=False)

    # Cart Items (junction table)
    op.create_table('cart_items',
        sa.Column('u_id', sa.String(), nullable=False),
        sa.Column('p_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['u_id'], ['users.u_id']),
        sa.ForeignKeyConstraint(['p_id'], ['product_items.p_id']),
        sa.PrimaryKeyConstraint('u_id', 'p_id'),
    )

    # Submissions
    op.create_table('submissions',
        sa.Column('sub_id', sa.String(), nullable=False),
        sa.Column('u_id', sa.String(), nullable=False),
        sa.Column('receipt', sa.JSON(), nullable=True),
        sa.Column('is_confirmed', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['u_id'], ['users.u_id']),
        sa.PrimaryKeyConstraint('sub_id'),
    )
    op.create_index(op.f('ix_submissions_sub_id'), 'submissions', ['sub_id'], unique=False)

    # Submission Items
    op.create_table('submission_items',
        sa.Column('sub_item_id', sa.String(), nullable=False),
        sa.Column('p_id', sa.String(), nullable=False),
        sa.Column('sub_id', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['p_id'], ['product_items.p_id']),
        sa.ForeignKeyConstraint(['sub_id'], ['submissions.sub_id']),
        sa.PrimaryKeyConstraint('sub_item_id'),
    )
    op.create_index(op.f('ix_submission_items_sub_item_id'), 'submission_items', ['sub_item_id'], unique=False)

    # Price By Hour
    op.create_table('price_by_hour',
        sa.Column('p_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['p_id'], ['product_items.p_id']),
        sa.PrimaryKeyConstraint('p_id', 'timestamp'),
    )


def downgrade() -> None:
    # Drop new tables
    op.drop_table('price_by_hour')
    op.drop_index(op.f('ix_submission_items_sub_item_id'), table_name='submission_items')
    op.drop_table('submission_items')
    op.drop_index(op.f('ix_submissions_sub_id'), table_name='submissions')
    op.drop_table('submissions')
    op.drop_table('cart_items')
    op.drop_index(op.f('ix_product_items_p_id'), table_name='product_items')
    op.drop_table('product_items')
    op.drop_index(op.f('ix_users_u_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_stores_store_id'), table_name='stores')
    op.drop_table('stores')
    op.drop_index(op.f('ix_brands_brand_id'), table_name='brands')
    op.drop_table('brands')
    op.drop_index(op.f('ix_categories_c_id'), table_name='categories')
    op.drop_table('categories')

    # Note: Downgrade does not recreate old tables - would require full old schema
