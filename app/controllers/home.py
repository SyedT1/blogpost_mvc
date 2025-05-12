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
from app.binders import PageOptionsBinder
from domain.common import PageOptions

BlogModelIn: typing.Any = create_pydantic_model(table=BlogIn, model_name=" BlogModelIn")

BlogModelOut: typing.Any = create_pydantic_model(table=Blog, include_default_columns=True, model_name=" BlogModelIn")

BlogModelPartial: typing.Any = create_pydantic_model(
    table=Blog, model_name="BlogModelPartial", all_optional=True
)

class Home(Controller):
    @get("/")
    async def index(self, page_options: PageOptions = PageOptionsBinder(PageOptions),request: Request = None):
        try:
            page = int(page_options.page) if page_options.page else 1
            limit = int(page_options.limit) if page_options.limit else 5
            offset = (page - 1) * limit

            total = await Blog.count()
            blog = await Blog.select().order_by(Blog.datetime_of_update,ascending=False).limit(limit).offset(offset)
            pages = (total // limit) + (1 if total % limit else 0)
            username = None
            role = None
            if request.identity is not None:
                username = request.identity.claims.get("name")
                role = request.identity.claims.get("role")
            print(username)
            return self.view(
                blog=blog,
                page=page,
                limit=limit,
                total=total,
                pages=pages,
                username=username,
                role=role,
            )
        except Exception as e:
            return self.view(
                blog=[],
                page=1,
                limit=5,
                total=0,
                pages=1,
                error=str(e)
            )