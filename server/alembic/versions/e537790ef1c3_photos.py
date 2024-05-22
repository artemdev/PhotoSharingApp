"""Photos

Revision ID: e537790ef1c3
Revises: 48c9b4d0a799
Create Date: 2024-05-21 19:02:37.692238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e537790ef1c3'
down_revision: Union[str, None] = '48c9b4d0a799'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('comments', 'text',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=50),
               existing_nullable=False)
    op.drop_constraint('tags_name_key', 'tags', type_='unique')
    op.drop_constraint('tags_pictures_picture_id_fkey', 'tags_pictures', type_='foreignkey')
    op.drop_constraint('tags_pictures_tag_id_fkey', 'tags_pictures', type_='foreignkey')
    op.create_foreign_key(None, 'tags_pictures', 'tags', ['tag_id'], ['id'])
    op.create_foreign_key(None, 'tags_pictures', 'pictures', ['picture_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tags_pictures', type_='foreignkey')
    op.drop_constraint(None, 'tags_pictures', type_='foreignkey')
    op.create_foreign_key('tags_pictures_tag_id_fkey', 'tags_pictures', 'tags', ['tag_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('tags_pictures_picture_id_fkey', 'tags_pictures', 'pictures', ['picture_id'], ['id'], ondelete='CASCADE')
    op.create_unique_constraint('tags_name_key', 'tags', ['name'])
    op.alter_column('comments', 'text',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
    # ### end Alembic commands ###