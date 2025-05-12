from piccolo.table import Table
from piccolo.columns import Varchar, Timestamp
from piccolo.columns.column_types import TimestampNow

class Blog(Table):
    title = Varchar()
    description = Varchar()
    post = Varchar()
    datetime_of_creation = Timestamp(default=TimestampNow(), required=False)
    datetime_of_update = Timestamp(default=TimestampNow(), required=False, on_update=TimestampNow())


class BlogIn(Table):
    title = Varchar()
    description = Varchar()
    post = Varchar()



class UserInfo(Table):
    username = Varchar()
    password = Varchar()
    role = Varchar(default="user")  # "superadmin" or "user"