"""add_subscription_url_to_users

Revision ID: 728db1cb29a0
Revises: b95a048017a2
Create Date: 2026-04-25 13:05:43.038306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '728db1cb29a0'
down_revision: Union[str, Sequence[str], None] = 'b95a048017a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('subscription_url', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'subscription_url')
