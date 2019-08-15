"""empty message

Revision ID: 5b5c2c9b53c0
Revises: f77040475ccd
Create Date: 2019-08-15 13:19:33.724757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b5c2c9b53c0'
down_revision = 'f77040475ccd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game_data', sa.Column('dh_status', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game_data', 'dh_status')
    # ### end Alembic commands ###
