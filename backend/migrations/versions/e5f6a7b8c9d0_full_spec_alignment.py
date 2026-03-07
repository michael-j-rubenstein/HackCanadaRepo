"""full spec alignment: users, receipts, store geo, enriched price submissions, grocery item fields, user-scoped alerts/cart/pins

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-03-07 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Phase 1: Users table ---
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('trust_score', sa.Float(), server_default='1.0', nullable=True),
        sa.Column('submission_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('home_lat', sa.Float(), nullable=True),
        sa.Column('home_lng', sa.Float(), nullable=True),
        sa.Column('radius_km', sa.Integer(), server_default='10', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # --- Phase 3: Receipts table ---
    op.create_table('receipts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ocr_parsed_json', sa.JSON(), nullable=True),
        sa.Column('store_location_id', sa.Integer(), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(), server_default='pending', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['store_location_id'], ['stores.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_receipts_id'), 'receipts', ['id'], unique=False)

    # --- Phase 2: Store geo columns ---
    op.add_column('stores', sa.Column('lat', sa.Float(), nullable=True))
    op.add_column('stores', sa.Column('lng', sa.Float(), nullable=True))
    op.add_column('stores', sa.Column('city', sa.String(), nullable=True))
    op.add_column('stores', sa.Column('province', sa.String(), nullable=True))
    op.add_column('stores', sa.Column('postal_code', sa.String(), nullable=True))

    # --- Phase 5: Grocery item columns ---
    op.add_column('grocery_items', sa.Column('barcode', sa.String(), nullable=True))
    op.add_column('grocery_items', sa.Column('status', sa.String(), server_default='active', nullable=True))
    op.add_column('grocery_items', sa.Column('is_new', sa.Boolean(), server_default='true', nullable=True))
    op.add_column('grocery_items', sa.Column('confirmation_count', sa.Integer(), server_default='0', nullable=True))
    op.create_unique_constraint('uq_grocery_items_barcode', 'grocery_items', ['barcode'])

    # --- Phase 1: Alter submissions.user_id from String to Integer FK ---
    # Drop old index
    op.drop_index(op.f('ix_submissions_user_id'), table_name='submissions')
    # Alter column type (requires USING clause for Postgres)
    op.execute("ALTER TABLE submissions ALTER COLUMN user_id TYPE INTEGER USING user_id::INTEGER")
    op.create_foreign_key('fk_submissions_user_id', 'submissions', 'users', ['user_id'], ['id'])
    op.create_index(op.f('ix_submissions_user_id'), 'submissions', ['user_id'], unique=False)

    # --- Phase 3: Add receipt_id to submissions ---
    op.add_column('submissions', sa.Column('receipt_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_submissions_receipt_id', 'submissions', 'receipts', ['receipt_id'], ['id'])

    # --- Phase 4: Enrich price_submissions ---
    op.add_column('price_submissions', sa.Column('report_type', sa.String(), server_default='community', nullable=True))
    op.add_column('price_submissions', sa.Column('source', sa.String(), nullable=True))
    op.add_column('price_submissions', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('price_submissions', sa.Column('receipt_id', sa.Integer(), nullable=True))
    op.add_column('price_submissions', sa.Column('confidence', sa.Float(), server_default='1.0', nullable=True))
    op.add_column('price_submissions', sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('price_submissions', sa.Column('is_outlier', sa.Boolean(), server_default='false', nullable=True))
    op.create_foreign_key('fk_price_submissions_user_id', 'price_submissions', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_price_submissions_receipt_id', 'price_submissions', 'receipts', ['receipt_id'], ['id'])

    # --- Phase 12: User-scope alerts, cart, pins ---
    op.add_column('price_alerts', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_price_alerts_user_id', 'price_alerts', 'users', ['user_id'], ['id'])

    # Shopping cart: create table (was never migrated before)
    op.create_table('shopping_cart_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['grocery_items.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'item_id', name='uq_cart_user_item'),
    )
    op.create_index(op.f('ix_shopping_cart_items_id'), 'shopping_cart_items', ['id'], unique=False)

    # Pinned items: create table (was never migrated before)
    op.create_table('pinned_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['grocery_items.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'item_id', name='uq_pin_user_item'),
    )
    op.create_index(op.f('ix_pinned_items_id'), 'pinned_items', ['id'], unique=False)

    # --- Phase 8: Materialized views ---
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_product_price_daily AS
        SELECT item_id AS product_id,
               date_trunc('day', date_observed) AS price_date,
               AVG(price)::FLOAT AS avg_price,
               MIN(price) AS min_price,
               MAX(price) AS max_price,
               COUNT(*) AS report_count
        FROM price_submissions
        WHERE is_outlier = false
        GROUP BY item_id, date_trunc('day', date_observed)
    """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_product_price_daily
        ON mv_product_price_daily (product_id, price_date)
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_category_price_daily AS
        SELECT gi.category_id,
               date_trunc('day', ps.date_observed) AS price_date,
               AVG(ps.price)::FLOAT AS avg_price,
               MIN(ps.price) AS min_price,
               MAX(ps.price) AS max_price,
               COUNT(*) AS report_count
        FROM price_submissions ps
        JOIN grocery_items gi ON ps.item_id = gi.id
        WHERE ps.is_outlier = false
        GROUP BY gi.category_id, date_trunc('day', ps.date_observed)
    """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_category_price_daily
        ON mv_category_price_daily (category_id, price_date)
    """)


def downgrade() -> None:
    # Materialized views
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_category_price_daily")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_product_price_daily")

    # Pinned items
    op.drop_index(op.f('ix_pinned_items_id'), table_name='pinned_items')
    op.drop_table('pinned_items')

    # Shopping cart
    op.drop_index(op.f('ix_shopping_cart_items_id'), table_name='shopping_cart_items')
    op.drop_table('shopping_cart_items')

    # Price alerts
    op.drop_constraint('fk_price_alerts_user_id', 'price_alerts', type_='foreignkey')
    op.drop_column('price_alerts', 'user_id')

    # Price submissions enrichment
    op.drop_constraint('fk_price_submissions_receipt_id', 'price_submissions', type_='foreignkey')
    op.drop_constraint('fk_price_submissions_user_id', 'price_submissions', type_='foreignkey')
    op.drop_column('price_submissions', 'is_outlier')
    op.drop_column('price_submissions', 'is_verified')
    op.drop_column('price_submissions', 'confidence')
    op.drop_column('price_submissions', 'receipt_id')
    op.drop_column('price_submissions', 'user_id')
    op.drop_column('price_submissions', 'source')
    op.drop_column('price_submissions', 'report_type')

    # Submissions receipt_id
    op.drop_constraint('fk_submissions_receipt_id', 'submissions', type_='foreignkey')
    op.drop_column('submissions', 'receipt_id')

    # Submissions user_id back to String
    op.drop_constraint('fk_submissions_user_id', 'submissions', type_='foreignkey')
    op.drop_index(op.f('ix_submissions_user_id'), table_name='submissions')
    op.execute("ALTER TABLE submissions ALTER COLUMN user_id TYPE VARCHAR USING user_id::VARCHAR")
    op.create_index(op.f('ix_submissions_user_id'), 'submissions', ['user_id'], unique=False)

    # Grocery items
    op.drop_constraint('uq_grocery_items_barcode', 'grocery_items', type_='unique')
    op.drop_column('grocery_items', 'confirmation_count')
    op.drop_column('grocery_items', 'is_new')
    op.drop_column('grocery_items', 'status')
    op.drop_column('grocery_items', 'barcode')

    # Store geo
    op.drop_column('stores', 'postal_code')
    op.drop_column('stores', 'province')
    op.drop_column('stores', 'city')
    op.drop_column('stores', 'lng')
    op.drop_column('stores', 'lat')

    # Receipts table
    op.drop_index(op.f('ix_receipts_id'), table_name='receipts')
    op.drop_table('receipts')

    # Users table
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
