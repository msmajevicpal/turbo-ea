"""Remove the TurboLens CVE scanner feature.

Drops the ``turbolens_cve_findings`` table, purges TurboLens analysis runs that
recorded CVE scans, and removes risks that were promoted from CVE findings
(along with their card joins and the system Todos that were linked to those
risks). The Compliance scanner is unaffected.

Revision ID: 084
Revises: 083
Create Date: 2026-05-14
"""

from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "084"
down_revision: Union[str, None] = "083"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM risk_cards WHERE risk_id IN ("
            "SELECT id FROM risks WHERE source_type = 'security_cve')"
        )
    )
    op.execute(
        sa.text(
            "DELETE FROM todos WHERE is_system = true AND link IN ("
            "SELECT '/ea-delivery/risks/' || id::text FROM risks "
            "WHERE source_type = 'security_cve')"
        )
    )

    op.drop_index("ix_turbolens_cve_findings_risk_id", table_name="turbolens_cve_findings")
    op.drop_index("ix_turbolens_cve_findings_priority", table_name="turbolens_cve_findings")
    op.drop_index("ix_turbolens_cve_findings_severity", table_name="turbolens_cve_findings")
    op.drop_index("ix_turbolens_cve_findings_cve_id", table_name="turbolens_cve_findings")
    op.drop_index("ix_turbolens_cve_findings_status", table_name="turbolens_cve_findings")
    op.drop_index("ix_turbolens_cve_findings_run_id", table_name="turbolens_cve_findings")
    op.drop_index(
        "ix_turbolens_cve_findings_card_id_severity",
        table_name="turbolens_cve_findings",
    )
    op.drop_table("turbolens_cve_findings")

    op.execute(sa.text("DELETE FROM risks WHERE source_type = 'security_cve'"))
    op.execute(sa.text("DELETE FROM turbolens_analysis_runs WHERE analysis_type = 'security_cve'"))


def downgrade() -> None:
    raise NotImplementedError(
        "The CVE scanner feature has been removed permanently; this migration is one-way."
    )
