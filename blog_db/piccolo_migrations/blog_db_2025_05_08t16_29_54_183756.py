from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod


ID = "2025-05-08T16:29:54:183756"
VERSION = "1.25.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="blog_db", description=DESCRIPTION
    )

    manager.add_column(
        table_class_name="User",
        tablename="user",
        column_name="role",
        db_column_name="role",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "user",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager
