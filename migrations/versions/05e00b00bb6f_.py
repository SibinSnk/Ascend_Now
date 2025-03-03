"""empty message

Revision ID: 05e00b00bb6f
Revises: d4b44d6c7e5c
Create Date: 2025-02-24 20:18:22.940780

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '05e00b00bb6f'
down_revision = 'd4b44d6c7e5c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exam', schema=None) as batch_op:
        batch_op.add_column(sa.Column('section_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_exam_section', 'section', ['section_id'], ['id'])  # Explicit FK name

    # ### end Alembic commands ###



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exam', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('section_id')

    # ### end Alembic commands ###
