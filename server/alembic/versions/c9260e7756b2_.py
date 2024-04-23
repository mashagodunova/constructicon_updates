"""

Revision ID: c9260e7756b2
Revises: 6a8362c400dc
Create Date: 2024-04-15 19:12:17.271913

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = 'c9260e7756b2'
down_revision = '6a8362c400dc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('token', schema=None) as batch_op:
        batch_op.drop_index('ix_token_id')

    op.drop_table('token')
    with op.batch_alter_table('glossindex', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_glossindex_construction_id'), ['construction_id'], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('glossindex', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_glossindex_construction_id'))

    op.create_table('token',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), nullable=False),
    sa.Column('last_usage', sa.DATETIME(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_token_user_id_user'),
    sa.PrimaryKeyConstraint('id', name='pk_token')
    )
    with op.batch_alter_table('token', schema=None) as batch_op:
        batch_op.create_index('ix_token_id', ['id'], unique=False)

    # ### end Alembic commands ###