import abc
import logging
from dataclasses import dataclass, field
from typing import Sequence, Optional, List

from pydantic import BaseModel

from food_truck.backend.eventstore.event_store import Event, EventsToRecord
from food_truck.backend.pipelines.message import (
    AbstractMessage,
    CommandStatus,
    QueryResult,
    Command,
)

_log = logging.getLogger(__name__)


@dataclass(kw_only=True)
class AbstractMessageContextModel(abc.ABC):
    version: int = field(default=0)  # optimistic concurrency control


class AbstractContextManager(abc.ABC):

    STREAM = [Event]

    def __init__(self, version: Optional[int] = 0) -> None:
        self.version = version
        _log.debug(self.__class__.__name__)

    @abc.abstractmethod
    def load(self, message: AbstractMessage) -> AbstractMessageContextModel:
        """context loader"""
        raise NotImplementedError

    def update(self, events: Sequence[Event]) -> None:
        """context builder
        All contexts and context models are read-only.
        If changes are made to them during the message processing stage, they will be discarded after restart.
        Changes to the application state have to be encoded in events written to the event stream
        """
        for e in events:
            if type(e) in self.STREAM:  # update stream version
                self.version = e.version
            self._apply(e)

    @abc.abstractmethod
    def _apply(self, event: Event):
        raise NotImplementedError


class Output(BaseModel):
    pass


class CommandOutput(Output):
    status: CommandStatus
    evtr: Optional[EventsToRecord]


class QueryOutput(Output):
    result: QueryResult


class NotificationOutput(Output):
    commands: List[Command]


class AbstractProcessor(abc.ABC):
    @abc.abstractmethod
    def process(
        self, input: AbstractMessage, model: AbstractMessageContextModel
    ) -> Output:
        raise NotImplementedError
