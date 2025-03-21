"""Contact email added

Revision ID: 6bf589812c91
Revises: 3861ac3a1ae4
Create Date: 2025-03-18 14:37:51.063600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6bf589812c91'
down_revision: Union[str, None] = '3861ac3a1ae4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('email', sa.String(), nullable=False))
    op.alter_column('contacts', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('contacts', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('contacts', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.create_unique_constraint(None, 'contacts', ['email'])
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('users', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_constraint(None, 'contacts', type_='unique')
    op.alter_column('contacts', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('contacts', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('contacts', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('contacts', 'email')
    # ### end Alembic commands ###
