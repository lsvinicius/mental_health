"""initial user

Revision ID: e9a7a8181c20
Revises: 1ee6ddced4f0
Create Date: 2026-01-09 19:34:37.007069

"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e9a7a8181c20"
down_revision: Union[str, Sequence[str], None] = "1ee6ddced4f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        f"INSERT INTO users (name, email, id) VALUES ('Vini', 'vini@example.com', '{uuid4()}');"
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
