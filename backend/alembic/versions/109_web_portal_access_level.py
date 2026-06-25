"""Add ``access_level`` to web portals.

Web portals gain a three-state access control — ``public`` (anyone),
``authenticated`` (any logged-in user), or ``disabled`` (not served) —
replacing the binary published/unpublished model. ``is_published`` is kept
in sync (True when access_level != 'disabled') for backward compatibility.

Existing rows are backfilled: published → 'public', otherwise → 'disabled'.

Revision ID: 109
Revises: 108
Create Date: 2026-06-25
"""

from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "109"
down_revision: Union[str, None] = "108"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.add_column(
        "web_portals",
        sa.Column(
            "access_level",
            sa.String(length=20),
            nullable=False,
            server_default="disabled",
        ),
    )
    op.execute(
        "UPDATE web_portals SET access_level = "
        "CASE WHEN is_published THEN 'public' ELSE 'disabled' END"
    )


def downgrade() -> None:
    op.drop_column("web_portals", "access_level")
