"""Add modified and completion percentage columns to survey statistics.

Revision ID: 20220921134624
Revises:
Create Date: 2022-09-21 11:42:25.215599
"""
from alembic import op
from osha.oira.upgrade.utils import has_column

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20220921134624"
down_revision = None
branch_labels = None
depends_on = None


def upgrade(engine_name):
    if not has_column("assessment", "modified"):
        op.add_column("assessment", sa.Column("modified", sa.DateTime(), nullable=True))
    if not has_column("assessment", "completion_percentage"):
        op.add_column(
            "assessment",
            sa.Column("completion_percentage", sa.Integer(), nullable=True, default=0),
        )


def downgrade(engine_name):
    if has_column("assessment", "modified"):
        op.drop_column("assessment", "modified")
    if has_column("assessment", "completion_percentage"):
        op.drop_column("assessment", "completion_percentage")
