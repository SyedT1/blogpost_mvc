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
from blog_db.tables import Category,Tag, BlogTag, UserInfo
from app.binders import PageOptionsBinder
from domain.common import PageOptions
from datetime import datetime

BlogModelIn: typing.Any = create_pydantic_model(table=BlogIn, model_name=" BlogModelIn")

BlogModelOut: typing.Any = create_pydantic_model(table=Blog, include_default_columns=True, model_name=" BlogModelIn")

BlogModelPartial: typing.Any = create_pydantic_model(
    table=Blog, model_name="BlogModelPartial", all_optional=True
)
from datetime import datetime

def time_ago(dt):
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    now = datetime.now()  # System local time
    diff = now - dt

    seconds = diff.total_seconds()
    minutes = int(seconds // 60)
    hours = int(seconds // 3600)
    days = int(seconds // 86400)

    if seconds < 60:
        return "just now"
    elif minutes == 1:
        return "a minute ago"
    elif minutes < 60:
        return f"{minutes} minutes ago"
    elif hours == 1:
        return "an hour ago"
    elif hours < 24:
        return f"{hours} hours ago"
    elif days == 1:
        return "a day ago"
    elif days < 7:
        return f"{days} days ago"
    else:
        return dt.strftime("%d %b %Y, %I:%M %p")

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
            print(blog)
            for item in blog:
                item["formatted_datetime_of_creation"] = time_ago(item["datetime_of_creation"])
                # # Fetch category name
                category = await Category.select(Category.name).where(Category.id == item["category"]).first()
                item["category_name"] = category["name"] if category else "Uncategorized"
                # # Fetch author name
                author = await UserInfo.select(UserInfo.username).where(UserInfo.id == item["author_id"]).first()
                item["author_name"] = author["username"] if author else "Unknown"
                # print(item["author_name"])
                # # Fetch tags
                # tags = await BlogTag.select(BlogTag.tag.name).where(BlogTag.blog == item["id"])
                # item["tags"] = [tag["name"] for tag in tags] if tags else []
                # print(tags)
                tags = await BlogTag.select(BlogTag.tag.name).where(BlogTag.blog == item["id"])
                item["tags"] = [tag["tag.name"] for tag in tags] if tags else []
                print(item["tags"])
            print(username)
            categories = await Category.select().run()
            top_tags = await Tag.select().limit(10).run()
            return self.view(
                blog=blog,
                page=page,
                limit=limit,
                total=total,
                pages=pages,
                username=username,
                role=role,
                categories=categories,
                top_tags=top_tags,
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