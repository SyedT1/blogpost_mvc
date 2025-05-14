"""
Common domain models reused across several API endpoints.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, conint

T = TypeVar("T")


@dataclass(slots=True)
class PaginatedSet(Generic[T]):
    items: list[T]
    total: int

    def __iter__(self):
        yield from self.items

    def __len__(self) -> int:
        return len(self.items)


@dataclass(slots=True)
class SetterAction(Generic[T]):
    """
    Describes an action that requires adding and removing objects from a collection.
    """

    add: list[T] = field(default_factory=list)
    remove: list[T] = field(default_factory=list)


class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"


class PageOptions(BaseModel):
    """
    Common pagination options for all endpoints implementing pagination of
    results.

    - page, for page number
    - limit, for results per page
    - continuation_id, the last numeric ID that was read
    """

    page: conint(gt=0) = Field(1, description="Page number.")  # type: ignore
    limit: conint(gt=0, le=1000) = Field(  # type: ignore
        100, description="Maximum number of results per page."
    )
    continuation_id: int | None = Field(
        None, description="If provided, the ID of the last object that was retrieved."
    )
    sort_order: SortOrder = SortOrder.ASC


class TimedMixin(BaseModel):
    created_at: datetime
    updated_at: datetime
    etag: str


class TimeFormatter(BaseModel):
    """
    Model to represent a datetime and its human-readable 'time ago' string.
    """
    original_datetime: datetime
    time_ago: str

    @classmethod
    def from_datetime(cls, dt: datetime | str):
        if isinstance(dt, str):
            dt_obj = datetime.fromisoformat(dt)
        else:
            dt_obj = dt
        now = datetime.now()
        diff = now - dt_obj

        seconds = diff.total_seconds()
        minutes = int(seconds // 60)
        hours = int(seconds // 3600)
        days = int(seconds // 86400)

        if seconds < 60:
            time_ago_str = "just now"
        elif minutes == 1:
            time_ago_str = "a minute ago"
        elif minutes < 60:
            time_ago_str = f"{minutes} minutes ago"
        elif hours == 1:
            time_ago_str = "an hour ago"
        elif hours < 24:
            time_ago_str = f"{hours} hours ago"
        elif days == 1:
            time_ago_str = "a day ago"
        elif days < 7:
            time_ago_str = f"{days} days ago"
        else:
            time_ago_str = dt_obj.strftime("%d %b %Y, %I:%M %p")

        return cls(original_datetime=dt_obj, time_ago=time_ago_str)


