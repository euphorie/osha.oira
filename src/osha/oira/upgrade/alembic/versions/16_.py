"""empty message

Revision ID: 16
Revises:
Create Date: 2020-04-24 15:44:55.552243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "16"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "certificate",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("json", sa.UnicodeText(), nullable=True),
        sa.Column("secret", sa.UnicodeText(), nullable=True),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["session.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_certificate_session_id"), "certificate", ["session_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_certificate_session_id"), table_name="certificate")
    op.drop_table("certificate")
    # ### end Alembic commands ###
