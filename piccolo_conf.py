from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

DB = PostgresEngine(
    config={
        "database": "postgres",
        "user": "postgres",
        "password": "root",
        "host": "localhost",
        "port": 5432,
    }
)
APP_REGISTRY = AppRegistry(apps=["blog_db.piccolo_app"])
