"""empty message

Revision ID: d4b44d6c7e5c
Revises: 2fa6ec8e0e4f
Create Date: 2025-02-24 20:02:52.463174

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd4b44d6c7e5c'
down_revision = '2fa6ec8e0e4f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exam',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('class_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('exam_type', sa.Enum('Midterm', 'Final', 'Quiz', 'Assignment', name='exam_types'), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['class_id'], ['class.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mark',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.Column('exam_id', sa.Integer(), nullable=False),
    sa.Column('marks_obtained', sa.Float(), nullable=False),
    sa.Column('total_marks', sa.Float(), nullable=False),
    sa.Column('grade', sa.String(length=5), nullable=False),
    sa.ForeignKeyConstraint(['exam_id'], ['exam.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('marks')
    op.drop_table('exams')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exams',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('class_id', sa.INTEGER(), nullable=False),
    sa.Column('exam_type', sa.VARCHAR(length=10), nullable=False),
    sa.Column('exam_date', sa.DATE(), nullable=False),
    sa.Column('subject', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['class_id'], ['class.id'], ),
    sa.ForeignKeyConstraint(['subject'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('marks',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('student_id', sa.INTEGER(), nullable=False),
    sa.Column('subject_id', sa.INTEGER(), nullable=False),
    sa.Column('exam_type', sa.VARCHAR(length=10), nullable=False),
    sa.Column('marks_obtained', sa.FLOAT(), nullable=False),
    sa.Column('total_marks', sa.FLOAT(), nullable=False),
    sa.Column('grade', sa.VARCHAR(length=5), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['student.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('mark')
    op.drop_table('exam')
    # ### end Alembic commands ###
