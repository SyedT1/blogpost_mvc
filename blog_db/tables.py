from piccolo.table import Table
from piccolo.columns import Varchar, Timestamp, Integer, Column, ForeignKey, Text
from piccolo.columns.column_types import TimestampNow

class Category(Table):
    name = Varchar(unique=True)

class Tag(Table):
    name = Varchar(unique=True)

class UserInfo(Table):
    username = Varchar()
    password = Varchar()
    role = Varchar(default="user")  # "superadmin" or "user"

    
class Blog(Table):
    title = Varchar()
    description = Varchar()
    post = Varchar()
    author_id = Integer()
    category = ForeignKey(references=Category)
    datetime_of_creation = Timestamp(default=TimestampNow(), required=False)
    datetime_of_update = Timestamp(default=TimestampNow(), required=False, on_update=TimestampNow())


class BlogIn(Table):
    title = Varchar()
    description = Varchar()
    post = Varchar()


class BlogTag(Table):
    blog = ForeignKey(references=Blog)
    tag = ForeignKey(references=Tag)


class Comment(Table):
    post = ForeignKey(references=Blog)
    author = ForeignKey(references=UserInfo)
    content = Varchar()
    datetime_of_creation = Timestamp(default=TimestampNow(), required=False)


class ChatMessage(Table):
    user = ForeignKey(references=UserInfo)
    channel_id = Integer()
    text = Text()
    datetime_of_creation = Timestamp(default=TimestampNow(), required=False)