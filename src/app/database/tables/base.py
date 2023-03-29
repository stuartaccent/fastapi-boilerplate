from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class all tables to inherit from
    https://docs.sqlalchemy.org/en/latest/orm/mapping_api.html#sqlalchemy.orm.declarative_base
    - example usage::
        from app.database.tables.base import Base
        class MyTable(Base)
            pass
    """
