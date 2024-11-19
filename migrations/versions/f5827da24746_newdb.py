"""newdb

Revision ID: f5827da24746
Revises: 
Create Date: 2024-11-17 18:26:17.646713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5827da24746'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('moallim',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('its', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('its')
    )
    op.create_table('daur',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('moallim_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['moallim_id'], ['moallim.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('student',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('its', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('grade', sa.String(length=1), nullable=False),
    sa.Column('daur_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['daur_id'], ['daur.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('its')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('student')
    op.drop_table('daur')
    op.drop_table('moallim')
    # ### end Alembic commands ###
