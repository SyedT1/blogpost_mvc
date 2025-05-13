from blacksheep.server.controllers import Controller, get, post
from blacksheep.server.responses import view, redirect, json
from blacksheep.cookies import Cookie
from blacksheep.server.authorization import auth
from blog_db.tables import UserInfo
from app.binders import PageOptionsBinder
from domain.common import PageOptions
from blog_db.tables import UserInfo
from blacksheep.server.controllers import Controller, get
from blacksheep import Request
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"  # Use a strong, random key in production

class User(Controller):

    @get("/login")
    async def login(self):
        return self.view("login", {"error": None})

    @post("/login")
    async def login_post(self, request):
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        user = await UserInfo.select().where(
            (UserInfo.username == username) & (UserInfo.password == password)
        ).first()
        # print(user["role"])
        if user:
            token = jwt.encode(
                {"sub": username, "role": user["role"], "id": user["id"]},
                SECRET_KEY,
                algorithm="HS256"
            )
            # print("redirected first")
            response = redirect("/")
            response.set_cookie(Cookie("access_token", token, http_only=True,path="/"))
            # print("redirected continued")
            return response
        else:
            return self.view("login", {"error": "Invalid username or password."})

    @auth("authenticated")
    @get("/logout")
    async def logout(self):
        response = redirect("/")
        response.set_cookie(
            Cookie(
                "access_token",
                "",
                expires=datetime.now() - timedelta(days=1),
                http_only=True,
                path="/"
            )
        )
        return response

    @auth("authenticated")
    @get("/manage_user")
    async def manage_users(
        self,
        page_options: PageOptions = PageOptionsBinder(PageOptions),
        request: Request = None
    ):
        if request.identity.claims.get("role") != "superadmin":
            return self.view("error", {"error": "Forbidden"})

        try:
            page = int(page_options.page) if page_options.page else 1
            limit = int(page_options.limit) if page_options.limit else 10
            offset = (page - 1) * limit
            search_value = request.query.get("search")
            sort_by = "id" if not isinstance(request.query.get("sort_by"), list) else request.query.get("sort_by")[0]
            sort_dir = "asc" if not isinstance(request.query.get("sort_dir"), list) else request.query.get("sort_dir")[0]
            map_of_sort_by = {
                "id": UserInfo.id,
                "username": UserInfo.username,
                "role": UserInfo.role
            }
            is_ascending = True if sort_dir == "asc" else False

            total = await UserInfo.count()
            users = None
            if search_value:
                search_value = search_value[0]
                string = f'%{search_value}%'
                users = await UserInfo.select().where(
                    UserInfo.username.ilike(string)
                ).order_by(map_of_sort_by[sort_by], ascending=is_ascending).limit(limit).offset(offset)
                total = await UserInfo.count().where(UserInfo.username.ilike(string))
            else:
                users = await UserInfo.select().order_by(map_of_sort_by[sort_by], ascending=is_ascending).limit(limit).offset(offset)

            pages = (total // limit) + (1 if total % limit else 0)

            return self.view(
                "manage_user",
                users=users,
                page=page,
                limit=limit,
                total=total,
                pages=pages,
                sort_by=sort_by,
                sort_dir=sort_dir
            )
        except Exception as e:
            return self.view(
                "manage_user",
                users=[],
                page=1,
                limit=10,
                total=0,
                pages=1,
                error=str(e)
            )

    @auth("authenticated")
    @get("/create_user")
    async def create_user_get(self, request):
        # Only superadmin can access
        if request.identity.claims.get("role") != "superadmin":
            return self.view("error", {"error": "Forbidden"})
        return self.view("create_user_get", {"error": None, "success": None})

    @auth("authenticated")
    @post("/create_user")
    async def create_user_post(self, request):
        if request.identity.claims.get("role") != "superadmin":
            return self.view("error", {"error": "Forbidden"})
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        role = form.get("role", "user")
        exists = await UserInfo.exists().where(UserInfo.username == username)
        print(username,password,role)
        if exists:
            return view("user/create_user_get", {"error": "User already exists", "success": None})
        await UserInfo(username=username, password=password, role=role).save()
        return redirect("/manage_user")

    @post("/delete_user/{user_id}")
    async def delete_blog(self, user_id: int):
        print("delete")
        try:
            await UserInfo.delete().where(UserInfo.id == user_id)
            print("hereeee manage")
            return redirect("/manage_user")
        except Exception as e:
            return self.view(error=str(e))