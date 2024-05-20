"""Add foreign key to tags_pictures table

Revision ID: 11d434165206
Revises: ad090f5ad058
Create Date: 2024-05-18 22:30:22.912972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11d434165206'
down_revision: Union[str, None] = 'ad090f5ad058'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
