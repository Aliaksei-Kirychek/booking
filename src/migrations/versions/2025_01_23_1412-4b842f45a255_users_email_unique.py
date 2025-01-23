"""users email unique

Revision ID: 4b842f45a255
Revises: d7ae1eb9e4b9
Create Date: 2025-01-23 14:12:27.988672

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4b842f45a255"
down_revision: Union[str, None] = "d7ae1eb9e4b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")
