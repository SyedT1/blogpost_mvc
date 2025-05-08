from blacksheep.server.controllers import Controller, get, post, delete, put
from blacksheep.server.bindings import FromForm, FromJson
from blacksheep import Request, redirect, Response
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

class Manage(Controller):
    @get("/load_table")
    async def load_tab(self, page_options: PageOptions = PageOptionsBinder(PageOptions), request: Request = None):
        try:
            page = int(page_options.page) if page_options.page else 1
            limit = int(page_options.limit) if page_options.limit else 5
            offset = (page - 1) * limit
            search_value = request.query.get("search")
            # Get sort params from query
            sort_by = "id" if not isinstance(request.query.get("sort_by"),list) else request.query.get("sort_by")[0]
            sort_dir =  "asc" if not isinstance(request.query.get("sort_dir"),list) else request.query.get("sort_dir")[0]
            map_of_sort_by = {
                "id" : Blog.id,
                "datetime_of_creation": Blog.datetime_of_creation,
                "datetime_of_update": Blog.datetime_of_update
            }
            is_ascending = True if sort_dir == "asc" else False

            total = await Blog.count()
            print(search_value)
            blog = None
            if search_value:
                search_value = search_value[0]
                string = f'%{search_value}%'
                blog = await Blog.select().where(Blog.title.ilike(string) | Blog.description.ilike(string)).order_by(map_of_sort_by[sort_by], ascending=is_ascending).limit(limit).offset(offset)
                total = await Blog.count().where(Blog.title.ilike(string))
            else:
                blog = await Blog.select().order_by(map_of_sort_by[sort_by], ascending=is_ascending).limit(limit).offset(offset)
            print(blog)
            pages = (total // limit) + (1 if total % limit else 0)

            return self.view(
                blog=blog,
                page=page,
                limit=limit,
                total=total,
                pages=pages,
                sort_by=sort_by,
                sort_dir=sort_dir
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