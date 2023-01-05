"""Add newsletter subscriptions.

Revision ID: 20221118124144
Revises: 16
Create Date: 2022-11-18 12:35:23.904586
"""
from alembic import op
from euphorie.deployment.upgrade.utils import has_table

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20221118124144"
down_revision = "16"
branch_labels = None
depends_on = None


def upgrade():
    if not has_table("newsletter_subscription"):
        op.create_table(
            "newsletter_subscription",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("account_id", sa.Integer(), nullable=False),
            sa.Column("zodb_path", sa.String(length=512), nullable=False),
            sa.ForeignKeyConstraint(
                ["account_id"], ["account.id"], onupdate="CASCADE", ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade():
    if has_table("newsletter_subscription"):
        op.drop_table("newsletter_subscription")
