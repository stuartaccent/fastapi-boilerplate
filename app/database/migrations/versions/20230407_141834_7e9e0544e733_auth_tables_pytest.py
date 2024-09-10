"""auth tables pytest

Revision ID: 7e9e0544e733
Revises: 
Create Date: 2023-04-07 14:18:34.819439

"""
import os
import sys

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "7e9e0544e733"
down_revision = None
branch_labels = None
depends_on = None


def is_pytest_running():
    return any("pytest" in arg for arg in sys.argv)


def upgrade():
    if not is_pytest_running():
        return

    script_dir = os.path.dirname(os.path.dirname(__file__))
    sql_file_path = os.path.join(script_dir, "sql", "create_auth_tables.sql")

    with open(sql_file_path, "r") as f:
        sql = f.read()

    for statement in sql.split(";"):
        op.execute(text(statement)) if statement.strip() else None


def downgrade():
    pass
