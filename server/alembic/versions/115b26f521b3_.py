"""

Revision ID: 115b26f521b3
Revises: c27a85766bc5
Create Date: 2023-02-11 16:22:33.865786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '115b26f521b3'
down_revision = 'c27a85766bc5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('syntacticstructure',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.Text(length=16), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('equivalent',
    sa.Column('construction_id', sa.Integer(), nullable=False),
    sa.Column('language', sa.Enum('english', 'russian', 'norwegian', name='language'), nullable=False),
    sa.Column('value', sa.UnicodeText(), nullable=False),
    sa.ForeignKeyConstraint(['construction_id'], ['construction.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('construction_id', 'language')
    )
    op.create_table('syntacticstructure2construction',
    sa.Column('left_id', sa.Integer(), nullable=False),
    sa.Column('right_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['left_id'], ['syntacticstructure.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['right_id'], ['construction.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('left_id', 'right_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('syntacticstructure2construction')
    op.drop_table('equivalent')
    op.drop_table('syntacticstructure')
    # ### end Alembic commands ###