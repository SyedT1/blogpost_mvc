from blacksheep.server.controllers import Controller, get, post, delete,put
from blacksheep.server.bindings import FromForm , FromJson
from blacksheep import Request,redirect,Response
from dataclasses import dataclass
from blacksheep.server.responses import view
from piccolo.columns import Varchar, Timestamp, Column
from piccolo.columns.column_types import TimestampNow
from piccolo.engine import engine_finder
from piccolo.utils.pydantic import create_pydantic_model
from blog_db.tables import Blog, BlogIn
import typing


class Manage(Controller):
    @get("/load_table")
    async def load_tab(self):
        try:
            blog = await Blog.select()
            print(blog)
            return self.view(blog=blog)
        except Exception as e:
            return self.view(error=str(e))