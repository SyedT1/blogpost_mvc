from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2025-05-12T10:20:17:256674"
VERSION = "1.25.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="blog_db", description=DESCRIPTION
    )

    manager.rename_table(
        old_class_name="User",
        old_tablename="user",
        new_class_name="UserInfo",
        new_tablename="user_info",
        schema=None,
    )

    return manager
