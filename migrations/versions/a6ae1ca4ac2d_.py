"""empty message

Revision ID: a6ae1ca4ac2d
Revises: d3f1e64a9bad
Create Date: 2023-02-20 16:48:58.337916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a6ae1ca4ac2d"
down_revision = "d3f1e64a9bad"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("Artist", schema=None) as batch_op:
        batch_op.add_column(sa.Column("genres", sa.ARRAY(sa.String()), nullable=False))

    with op.batch_alter_table("Venue", schema=None) as batch_op:
        batch_op.add_column(sa.Column("genres", sa.ARRAY(sa.String()), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("Venue", schema=None) as batch_op:
        batch_op.drop_column("genres")

    with op.batch_alter_table("Artist", schema=None) as batch_op:
        batch_op.drop_column("genres")

    # ### end Alembic commands ###
