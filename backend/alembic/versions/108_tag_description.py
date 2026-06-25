"""Add ``description`` to tags.

Tags gain an optional free-text description (tag groups already had one),
surfaced in the metamodel Tags admin and the tag picker.

Revision ID: 108
Revises: 107
Create Date: 2026-06-25
"""

from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "108"
down_revision: Union[str, None] = "107"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.add_column("tags", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("tags", "description")
