from blacksheep.server.controllers import Controller, get, post, delete,put
from blacksheep.server.bindings import FromForm , FromJson
from blacksheep import Request,redirect
from dataclasses import dataclass
from blacksheep.server.responses import view
from piccolo.columns import Varchar, Timestamp, Column
from piccolo.columns.column_types import TimestampNow
from piccolo.engine import engine_finder
from piccolo.utils.pydantic import create_pydantic_model
from blog_db.tables import Blog, BlogIn
import typing

BlogModelIn: typing.Any = create_pydantic_model(table=BlogIn, model_name=" BlogModelIn")

BlogModelOut: typing.Any = create_pydantic_model(table=Blog, include_default_columns=True, model_name=" BlogModelIn")

BlogModelPartial: typing.Any = create_pydantic_model(
    table=Blog, model_name="BlogModelPartial", all_optional=True
)

class Home(Controller):
    @get("/")
    async def index(self):
        # Since the @get() decorator is used without arguments, the URL path
        # is by default "/"

        # Since the view function is called without parameters, the name is
        # obtained from the calling request handler: 'index',
        # -> /views/home/index.jinja
        try:
            blog = await Blog.select()
            return self.view(blog=blog)
        except Exception as e:
            return self.view(error=str(e))
    @get("/create_blog")
    async def create(self):
        return self.view()
    @post("/create_blog")
    async def create_blog_post(self, request: Request):
        form = await request.form()
        title = form.get("title", "").strip()
        description = form.get("description", "").strip()
        post_content = form.get("post", "").strip()
        await Blog.insert(
            Blog(title=title, description=description or None, post=post_content)
        ) 
        return view("home/create")

    @post("/delete_item/{blog_id}")
    async def delete_blog(self, blog_id: int):
        try:
            await Blog.delete().where(Blog.id == blog_id)
            return redirect("/")
        except Exception as e:
            print("jonjal")
            return self.view(error=str(e))

    @get("/edit_blog/{blog_id}")
    async def edit_blog(self, blog_id: int):
        try:
            blog = await Blog.select().where(Blog.id == blog_id).first()
            if not blog:
                return self.view(error="Blog post not found.")
            return self.view("home/edit_blog", blog=blog)
        except Exception as e:
            return self.view(error=str(e))

    @post("/edit_blog/{blog_id}")
    async def update_blog(self, blog_id: int, request: Request):
        form = await request.form()
        title = form.get("title", "").strip()
        description = form.get("description", "").strip()
        post_content = form.get("post", "").strip()
        try:
            await Blog.update(
                {Blog.title: title, Blog.description: description, Blog.post: post_content}
            ).where(Blog.id == blog_id)
            return redirect("/")
        except Exception as e:
            return self.view(error=str(e))
