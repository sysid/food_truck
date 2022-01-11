import abc
from datetime import datetime

from pydantic import BaseModel, Field


# Message = Union[commands.Command, events.Event, notifications.Notification]


class AbstractMessage(abc.ABC, BaseModel):
    pass


class Request(AbstractMessage):
    created_at: datetime = Field(default_factory=datetime.now)


class Response(AbstractMessage):
    created_at: datetime = Field(default_factory=datetime.now)


class Notification(AbstractMessage):
    created_at: datetime = Field(default_factory=datetime.now)


class Command(Request):
    issued_at: datetime = Field(default_factory=datetime.now)


class Query(Request):
    pass


class CommandStatus(Response, abc.ABC):
    pass


class Success(CommandStatus):
    pass


class Failure(CommandStatus):
    error_message: str


class QueryResult(Response):
    pass


class NoResponse(Response):
    pass
