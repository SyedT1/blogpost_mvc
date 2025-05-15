from blacksheep.server.controllers import Controller, get, post, delete,put
from blacksheep.server.bindings import FromForm , FromJson
from blacksheep import Request,redirect,Response
from dataclasses import dataclass
from blacksheep.server.responses import view
from piccolo.columns import Varchar, Timestamp, Column
from piccolo.columns.column_types import TimestampNow
from piccolo.engine import engine_finder
from piccolo.utils.pydantic import create_pydantic_model
from blog_db.tables import Blog, BlogIn, UserInfo, Tag, BlogTag, Category, Comment
import typing
from blacksheep.server.authorization import auth
from domain.common import TimeFormatter
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

    @auth("authenticated")
    @get("/edit_blog/{blog_id}")
    async def edit(self, blog_id: int):
        try:
            blog = await Blog.select().where(Blog.id == blog_id).first()
            if not blog:
                return self.view(error="Blog post not found.")
            categories = await Category.select().run()
            top_tags = await Tag.select().limit(10).run()
            # Get current tags for this blog
            blog_tags = await BlogTag.select(BlogTag.tag).where(BlogTag.blog == blog_id).run()
            print(blog_tags)
            tags_ids = None
            current_tags = []
            if len(blog_tags) > 0:
                tag_ids = [bt["tag"] for bt in blog_tags]
                current_tags = await Tag.select(Tag.name).where(Tag.id.is_in(tag_ids)).run()
            return view('post/edit', blog=blog, categories=categories, top_tags=top_tags, current_tags=current_tags)
        except Exception as e:
            return self.view(error=str(e))

    @auth("authenticated")
    @post("/edit_blog/{blog_id}")
    async def update(self, blog_id: int, request: Request):
        print("hello")
        form = await request.form()
        title = form.get("title", "").strip()
        description = form.get("description", "").strip()
        post_content = form.get("post", "").strip()
        category_id = int(form.get("category"))
        updated_tag_names = [t.strip() for t in form.get("tags", "").split(",") if t.strip()]
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
            existing_tags = await BlogTag.select(BlogTag.tag).where(BlogTag.blog==blog_id)
            if len(existing_tags) > 0:
                existing_tags_list = [t["tag"] for t in existing_tags]
                await BlogTag.delete().where((BlogTag.tag.is_in(existing_tags_list)) & (BlogTag.blog == blog_id))
            if len(updated_tag_names) > 0:
                for tag_name in updated_tag_names:
                    tag = await Tag.select().where(Tag.name == tag_name).first()
                    if not tag:
                        tag = await Tag.insert(Tag(name=tag_name))
                    await BlogTag.insert(BlogTag(blog=blog_id, tag=tag["id"]))
            return redirect("/load_table")
        except Exception as e:
            print(e)
            return redirect("/")

    @auth("authenticated")
    @post("/delete_blog/{blog_id}")
    async def delete_blog(self, blog_id: int):
        print("delete")
        try:
            await Blog.delete().where(Blog.id == blog_id)
            await BlogTag.delete().where(BlogTag.blog == blog_id)
            print("hereeee")
            return redirect("/load_table")
        except Exception as e:
            return self.view(error=str(e))

    @get("/post/{post_id}")
    async def post_info(self, post_id: int, request: Request):
        try:
            blog = await Blog.select().where(Blog.id == post_id).first()
            # Fetch category name
            category_name = await Category.select(Category.name).where(Category.id == int(blog["category"]))
            blog["category"] = category_name[0]["name"] if category_name else "Uncategorized"
            # Fetch tags (list of strings)
            tags = await BlogTag.select(BlogTag.tag.name).where(BlogTag.blog == blog["id"])
            blog["tags"] = [tag["tag.name"] for tag in tags] if tags else []
            # Fetch author name
            author = await UserInfo.select(UserInfo.username).where(UserInfo.id == blog["author_id"]).first()
            blog["author_name"] = author["username"] if author else "Unknown"
            # Format creation date
            blog["formatted_datetime_of_creation"] = TimeFormatter.from_datetime(blog["datetime_of_creation"]).time_ago
            # Pass to template
            username = request.identity.claims.get("name") if request.identity else None
            print(username)
            comments = await Comment.select().where(Comment.post == post_id).order_by(Comment.datetime_of_creation, ascending=False)
            print(comments)
            for comment in comments:
                author = await UserInfo.select(UserInfo.username).where(UserInfo.id == int(comment["author"])).first()
                comment["author"] = author["username"]
                comment["formatted_datetime_of_creation"] = TimeFormatter.from_datetime(comment["datetime_of_creation"]).time_ago
            # username = await UserInfo.select(UserInfo.username).where(UserInfo.id == int(comments["author"])).first()
            return self.view(blog=blog,username=username,comments=comments)
        except Exception as e:
            print(e)
            return self.view(error=str(e))

    @auth("authenticated")
    @post("/add_comment/{blog_id}")
    async def comment(self, blog_id: int, request: Request):
        try:
            form = await request.form()
            content = form.get("content", "").strip()
            if not content:
                return self.view(error="Comment cannot be empty.")

            # Get user ID from token
            author_id = request.identity.claims.get("id")
            if not author_id:
                return self.view(error="User not authenticated.")

            # Save the comment
            await Comment.insert(
                Comment(
                    post=blog_id,
                    author=author_id,
                    content=content
                )
            )

            # Redirect back to the blog post page
            return redirect(f"/post/{blog_id}")

        except Exception as e:
            print(e)
            return self.view(error=str(e))

