from uuid import UUID

from sqlalchemy import text

user_type = {
    "id": UUID("1e071719-148a-4156-86d5-28f042186b99"),
    "name": "user",
}
user_type_sql = text(
    """
    INSERT INTO auth_user_types
    (
        id,
        name
    ) values (
        :id,
        :name
    )
"""
)
