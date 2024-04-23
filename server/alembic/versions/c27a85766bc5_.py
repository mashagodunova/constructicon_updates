"""

Revision ID: c27a85766bc5
Revises: bf85ffea75af
Create Date: 2022-12-18 20:21:59.856990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c27a85766bc5'
down_revision = 'bf85ffea75af'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_column('constructionexample', 'language')

    # fixed from here https://stackoverflow.com/questions/30394222/why-flask-migrate-cannot-upgrade-when-drop-column
    with op.batch_alter_table('constructionexample') as batch_op:
        batch_op.drop_column('language')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('constructionexample', sa.Column('language', sa.VARCHAR(length=9), nullable=False))
    # ### end Alembic commands ###