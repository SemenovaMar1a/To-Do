"""add_user_roles

Revision ID: 1ff06919a72e
Revises: f72bf0dfd209
Create Date: 2025-06-04 11:24:02.267396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ff06919a72e'
down_revision: Union[str, None] = 'f72bf0dfd209'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
    'users',
    sa.Column('role', sa.String(length=10), nullable=False, server_default='user')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
