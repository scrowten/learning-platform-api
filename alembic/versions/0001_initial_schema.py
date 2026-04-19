"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "domains",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("path", sa.String, nullable=False),
        sa.Column("color", sa.String),
        sa.Column("icon", sa.String),
        sa.Column("tags", sa.ARRAY(sa.Text)),
    )

    op.create_table(
        "modules",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("domain_id", sa.String, sa.ForeignKey("domains.id"), nullable=False),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("difficulty", sa.String),
        sa.Column("tags", sa.ARRAY(sa.Text)),
        sa.Column("estimated_hours", sa.Integer),
        sa.Column("git_path", sa.String),
        sa.Column("last_reviewed", sa.Date),
        sa.Column("sota_topics", sa.ARRAY(sa.Text)),
    )
    op.create_index("ix_modules_domain_id", "modules", ["domain_id"])

    op.create_table(
        "module_prerequisites",
        sa.Column("module_id", sa.String, sa.ForeignKey("modules.id"), primary_key=True),
        sa.Column("prereq_id", sa.String, sa.ForeignKey("modules.id"), primary_key=True),
    )

    op.create_table(
        "content_chunks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("module_id", sa.String, sa.ForeignKey("modules.id"), nullable=False),
        sa.Column("source_file", sa.String, nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
    )
    op.create_index("ix_content_chunks_module_id", "content_chunks", ["module_id"])

    op.create_table(
        "sync_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("domains_synced", sa.Integer, default=0),
        sa.Column("modules_synced", sa.Integer, default=0),
        sa.Column("error_message", sa.Text),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("sync_log")
    op.drop_table("content_chunks")
    op.drop_table("module_prerequisites")
    op.drop_table("modules")
    op.drop_table("domains")
