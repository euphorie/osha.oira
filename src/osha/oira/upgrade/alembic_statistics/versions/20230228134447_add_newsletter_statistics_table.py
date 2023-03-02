"""Add newsletter statistics table

Revision ID: 20230228134447
Revises: 20220921134624
Create Date: 2023-02-28 13:48:49.647245

"""
from alembic import op
from osha.oira.upgrade.utils import has_table

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20230228134447"
down_revision = "20220921134624"
branch_labels = None
depends_on = None


def upgrade(engine_name):
    if not has_table("newsletter"):
        op.create_table(
            "newsletter",
            sa.Column("zodb_path", sa.String(length=512), nullable=False),
            sa.Column("count", sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint("zodb_path"),
        )


def downgrade(engine_name):
    if has_table("newsletter"):
        op.drop_table("newsletter")
