from blacksheep.server.controllers import Controller, get, post, delete,put
from blacksheep.server.bindings import FromForm , FromJson
from blacksheep import Request,redirect,Response
from dataclasses import dataclass
from blacksheep.server.responses import view
from piccolo.columns import Varchar, Timestamp, Column
from piccolo.columns.column_types import TimestampNow
from piccolo.engine import engine_finder
from piccolo.utils.pydantic import create_pydantic_model
from blog_db.tables import Blog, BlogIn, UserInfo, Tag, BlogTag, Category
import typing
from blacksheep.server.authorization import auth

from app.binders import PageOptionsBinder
from domain.common import PageOptions
from datetime import datetime


class Post(Controller):
    @auth("authenticated")
    @get("/create_blog")
    async def create(self):
        categories = await Category.select().run()
        top_tags = await Tag.select().limit(10).run()
        return self.view(categories=categories, top_tags=top_tags)

    @auth("authenticated")
    @post("/create_blog")
    async def create_blog_post(self, request: Request):
        form = await request.form()
        title = form.get("title", "").strip()
        description = form.get("description", "").strip()
        post_content = form.get("post", "").strip()
        author_id = request.identity.claims.get("id")
        category_id = int(form.get("category"))
        tag_names = [t.strip() for t in form.get("tags", "").split(",") if t.strip()]

        # Create blog post
        blog = await Blog.insert(
            Blog(
                title=title,
                description=description or None,
                post=post_content,
                author_id=author_id,
                category=category_id
            )
        )
        # print(blog[0]['id'])
        for tag_name in tag_names:
            tag = await Tag.select().where(Tag.name == tag_name).first()
            if not tag:
                tag = await Tag.insert(Tag(name=tag_name))
            await BlogTag.insert(BlogTag(blog=blog[0]['id'], tag = tag['id'] if isinstance(tag,dict) else tag[0]['id']))
            # print(tag)
            # await BlogTag.insert(BlogTag(blog=blog[0]['id'], tag=tag.id))

        return redirect("/")


    @get("/edit_blog/{blog_id}")
    async def edit(self, blog_id: int):
        try:
            blog = await Blog.select().where(Blog.id == blog_id).first()
            if not blog:
                return self.view(error="Blog post not found.")
            categories = await Category.select().run()
            top_tags = await Tag.select().limit(10).run()
            # Get current tags for this blog
            blog_tags = await BlogTag.select().where(BlogTag.blog == blog_id).run()
            tag_ids = [bt.tag for bt in blog_tags]
            current_tags = await Tag.select().where(Tag.id.in_(tag_ids)).run()
            return view('post/edit', blog=blog, categories=categories, top_tags=top_tags, current_tags=current_tags)
        except Exception as e:
            return self.view(error=str(e))

    @post("/edit_blog/{blog_id}")
    async def update(self, blog_id: int, request: Request):
        form = await request.form()
        title = form.get("title", "").strip()
        description = form.get("description", "").strip()
        post_content = form.get("post", "").strip()
        category_id = int(form.get("category"))
        tag_names = [t.strip() for t in form.get("tags", "").split(",") if t.strip()]
        try:
            await Blog.update(
                {
                    Blog.title: title,
                    Blog.description: description,
                    Blog.post: post_content,
                    Blog.category: category_id,
                    Blog.datetime_of_update: datetime.now()
                }
            ).where(Blog.id == blog_id)

            # Update tags: remove old, add new
            await BlogTag.delete().where(BlogTag.blog == blog_id)
            for tag_name in tag_names:
                tag = await Tag.select().where(Tag.name == tag_name).first()
                if not tag:
                    tag = await Tag.insert(Tag(name=tag_name))
                await BlogTag.insert(BlogTag(blog=blog_id, tag=tag.id))

            return redirect("/load_table")
        except Exception as e:
            return view("home/index", error=str(e))

    @post("/delete_blog/{blog_id}")
    async def delete_blog(self, blog_id: int):
        print("delete")
        try:
            await Blog.delete().where(Blog.id == blog_id)
            print("hereeee")
            return redirect("/load_table")
        except Exception as e:
            return self.view(error=str(e))