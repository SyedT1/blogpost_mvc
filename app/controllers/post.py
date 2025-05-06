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



class Post(Controller):
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
        blog = await Blog.select()
        return view("home/index",blog=blog)


    @get("/edit_blog/{blog_id}")
    async def edit(self, blog_id: int):
        print("get request")
        try:
            blog = await Blog.select().where(Blog.id == blog_id).first()
            if not blog:
                return self.view(error="Blog post not found.")
            return view('post/edit',blog=blog)
        except Exception as e:
            return self.view(error=str(e))

    @post("/edit_blog/{blog_id}")
    async def update(self, blog_id: int, request: Request):
        print("post request")
        form = await request.form()
        title = form.get("title", "").strip()
        description = form.get("description", "").strip()
        post_content = form.get("post", "").strip()
        try:
            await Blog.update(
                {Blog.title: title, Blog.description: description, Blog.post: post_content}
            ).where(Blog.id == blog_id)
            blog = await Blog.select()
            return redirect("/")
        except Exception as e:
            return self.view(error=str(e))

    @post("/delete_blog/{blog_id}")
    async def delete_blog(self, blog_id: int):
        print("delete")
        try:
            await Blog.delete().where(Blog.id == blog_id)
            print("hereeee")
            return redirect("/load_table")
        except Exception as e:
            return self.view(error=str(e))