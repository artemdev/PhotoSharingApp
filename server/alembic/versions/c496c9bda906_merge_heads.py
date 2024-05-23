"""Merge heads

Revision ID: c496c9bda906
Revises: 0d694128dc41, 598e33f712e1
Create Date: 2024-05-23 00:20:25.511578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c496c9bda906'
down_revision: Union[str, None] = ('0d694128dc41', '598e33f712e1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
