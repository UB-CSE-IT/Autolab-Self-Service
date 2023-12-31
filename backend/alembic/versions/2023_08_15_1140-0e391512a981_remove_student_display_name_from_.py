"""

Remove student_display_name from CourseGradingAssignmentPair

Revision ID: 0e391512a981
Revises: e65fca53c6e4
Create Date: 2023-08-15 11:40:29.789279

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e391512a981'
down_revision = 'e65fca53c6e4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('course_grading_assignment_pairs', 'student_display_name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course_grading_assignment_pairs', sa.Column('student_display_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
