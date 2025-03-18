"""Fix asyncpg issue

Revision ID: 6efc8194a1e2
Revises: 1104c5de5729
Create Date: 2025-03-18 19:20:22.477492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6efc8194a1e2'
down_revision: Union[str, None] = '1104c5de5729'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('contacts_email_key', 'contacts', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('contacts_email_key', 'contacts', ['email'])
    # ### end Alembic commands ###
