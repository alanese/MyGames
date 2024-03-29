"""Initial tables

Revision ID: 625b7b7c5f11
Revises: 
Create Date: 2019-08-08 13:56:08.067939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '625b7b7c5f11'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('game_data',
    sa.Column('game_pk', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=10), nullable=True),
    sa.Column('home_team', sa.String(length=32), nullable=True),
    sa.Column('home_score', sa.Integer(), nullable=True),
    sa.Column('away_team', sa.String(length=32), nullable=True),
    sa.Column('away_score', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('game_pk')
    )
    op.create_index(op.f('ix_game_data_away_team'), 'game_data', ['away_team'], unique=False)
    op.create_index(op.f('ix_game_data_home_team'), 'game_data', ['home_team'], unique=False)
    op.create_table('player_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('sort_name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_player_data_name'), 'player_data', ['name'], unique=False)
    op.create_index(op.f('ix_player_data_sort_name'), 'player_data', ['sort_name'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('bat_game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_pk', sa.Integer(), nullable=True),
    sa.Column('batter_id', sa.Integer(), nullable=True),
    sa.Column('ab', sa.Integer(), nullable=True),
    sa.Column('r', sa.Integer(), nullable=True),
    sa.Column('h', sa.Integer(), nullable=True),
    sa.Column('doubles', sa.Integer(), nullable=True),
    sa.Column('triples', sa.Integer(), nullable=True),
    sa.Column('hr', sa.Integer(), nullable=True),
    sa.Column('rbi', sa.Integer(), nullable=True),
    sa.Column('sb', sa.Integer(), nullable=True),
    sa.Column('cs', sa.Integer(), nullable=True),
    sa.Column('k', sa.Integer(), nullable=True),
    sa.Column('bb', sa.Integer(), nullable=True),
    sa.Column('hbp', sa.Integer(), nullable=True),
    sa.Column('sf', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['batter_id'], ['player_data.id'], ),
    sa.ForeignKeyConstraint(['game_pk'], ['game_data.game_pk'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bat_game_batter_id'), 'bat_game', ['batter_id'], unique=False)
    op.create_index(op.f('ix_bat_game_game_pk'), 'bat_game', ['game_pk'], unique=False)
    op.create_table('game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_pk', sa.Integer(), nullable=True),
    sa.Column('game_result', sa.String(length=64), nullable=True),
    sa.Column('date', sa.String(length=10), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_pk'], ['game_data.game_pk'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_game_game_pk'), 'game', ['game_pk'], unique=False)
    op.create_table('pitch_game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_pk', sa.Integer(), nullable=True),
    sa.Column('pitcher_id', sa.Integer(), nullable=True),
    sa.Column('w', sa.Integer(), nullable=True),
    sa.Column('losses', sa.Integer(), nullable=True),
    sa.Column('gs', sa.Integer(), nullable=True),
    sa.Column('gf', sa.Integer(), nullable=True),
    sa.Column('sv', sa.Integer(), nullable=True),
    sa.Column('h', sa.Integer(), nullable=True),
    sa.Column('r', sa.Integer(), nullable=True),
    sa.Column('er', sa.Integer(), nullable=True),
    sa.Column('hr', sa.Integer(), nullable=True),
    sa.Column('bb', sa.Integer(), nullable=True),
    sa.Column('so', sa.Integer(), nullable=True),
    sa.Column('outs', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_pk'], ['game_data.game_pk'], ),
    sa.ForeignKeyConstraint(['pitcher_id'], ['player_data.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pitch_game_game_pk'), 'pitch_game', ['game_pk'], unique=False)
    op.create_index(op.f('ix_pitch_game_pitcher_id'), 'pitch_game', ['pitcher_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_pitch_game_pitcher_id'), table_name='pitch_game')
    op.drop_index(op.f('ix_pitch_game_game_pk'), table_name='pitch_game')
    op.drop_table('pitch_game')
    op.drop_index(op.f('ix_game_game_pk'), table_name='game')
    op.drop_table('game')
    op.drop_index(op.f('ix_bat_game_game_pk'), table_name='bat_game')
    op.drop_index(op.f('ix_bat_game_batter_id'), table_name='bat_game')
    op.drop_table('bat_game')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_player_data_sort_name'), table_name='player_data')
    op.drop_index(op.f('ix_player_data_name'), table_name='player_data')
    op.drop_table('player_data')
    op.drop_index(op.f('ix_game_data_home_team'), table_name='game_data')
    op.drop_index(op.f('ix_game_data_away_team'), table_name='game_data')
    op.drop_table('game_data')
    # ### end Alembic commands ###
