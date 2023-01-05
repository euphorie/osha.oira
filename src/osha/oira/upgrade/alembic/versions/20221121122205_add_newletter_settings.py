"""Add newletter settings.

Revision ID: 20221121122205
Revises: 20221118124144
Create Date: 2022-11-21 11:49:15.054453
"""
from alembic import op
from euphorie.deployment.upgrade.utils import has_table

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20221121122205"
down_revision = "20221118124144"
branch_labels = None
depends_on = None


def upgrade():
    if not has_table("newsletter_setting"):
        op.create_table(
            "newsletter_setting",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("account_id", sa.Integer(), nullable=False),
            sa.Column("value", sa.String(length=512), nullable=False),
            sa.ForeignKeyConstraint(
                ["account_id"], ["account.id"], onupdate="CASCADE", ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade():
    if has_table("newsletter_setting"):
        op.drop_table("newsletter_setting")
