"""

Revision ID: d85884e8e35a
Revises: c2f9883762b2
Create Date: 2023-03-30 14:22:21.097274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd85884e8e35a'
down_revision = 'c2f9883762b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('anchorpos', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_anchorpos_name'), ['name'])

    with op.batch_alter_table('morphologicaltag', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_morphologicaltag_name'), ['name'])

    with op.batch_alter_table('semanticrole', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_semanticrole_name'), ['name'])

    with op.batch_alter_table('semantictype', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_id', sa.Integer(), nullable=True))
        batch_op.create_unique_constraint(batch_op.f('uq_semantictype_name'), ['name'])
        batch_op.create_foreign_key(batch_op.f('fk_semantictype_parent_id_semantictype'), 'semantictype', ['parent_id'], ['id'])

    with op.batch_alter_table('syntacticfunction', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_syntacticfunction_name'), ['name'])

    with op.batch_alter_table('syntacticstructure', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_syntacticstructure_name'), ['name'])

    with op.batch_alter_table('syntactictype', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_syntactictype_name'), ['name'])

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('syntactictype', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_syntactictype_name'), type_='unique')

    with op.batch_alter_table('syntacticstructure', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_syntacticstructure_name'), type_='unique')

    with op.batch_alter_table('syntacticfunction', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_syntacticfunction_name'), type_='unique')

    with op.batch_alter_table('semantictype', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_semantictype_parent_id_semantictype'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('uq_semantictype_name'), type_='unique')
        batch_op.drop_column('parent_id')

    with op.batch_alter_table('semanticrole', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_semanticrole_name'), type_='unique')

    with op.batch_alter_table('morphologicaltag', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_morphologicaltag_name'), type_='unique')

    with op.batch_alter_table('anchorpos', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_anchorpos_name'), type_='unique')

    # ### end Alembic commands ###
