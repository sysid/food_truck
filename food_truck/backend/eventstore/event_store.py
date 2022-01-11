import abc
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Callable, Union, Type, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator

_log = logging.getLogger(__name__)


class Event(BaseModel):
    type_: Optional[str] = None
    id_: UUID = uuid4()
    created_at: datetime = Field(default_factory=datetime.now)
    version: int = 0  # optimistic concurrency control, managed by ES

    @validator("type_", pre=True, always=True)
    def add_type(cls, v) -> str:
        return cls.__name__


Stream = Optional[List[Type[Event]]]


class ReplayResult(BaseModel):
    version: int
    stream: Optional[Stream]
    events: List[Event]


class EventsToRecord(BaseModel):
    version: int
    stream: Stream
    events: List[Event]


class StreamVersionError(Exception):
    pass


class AbstractEventStore(abc.ABC):
    on_recorded: Callable[[List[Event]], None]

    def replay(self, stream: Stream = None) -> ReplayResult:
        """returns chronological stream of events"""
        _log.debug("Stream %s", stream if stream is not None else "all")
        events = self._load_events()
        if stream is not None:
            events = [e for e in events if type(e) in stream]

        return ReplayResult(
            version=events[-1].version if len(events) > 0 else 0,
            stream=stream,
            events=events,
        )

    @abc.abstractmethod
    def _load_events(self) -> List[Event]:
        raise NotImplementedError

    def record(self, evtr: EventsToRecord) -> None:
        _log.debug(evtr)
        self._stream_version_check(evtr.stream, evtr.version)
        self._record_events(evtr)
        self.on_recorded(evtr.events)

    def _stream_version_check(self, stream: Stream, version: int) -> None:
        replay_result = self.replay(stream)
        if replay_result.version != version:
            raise StreamVersionError(
                f"expected: {version}, current: {replay_result.version}"
            )

    @abc.abstractmethod
    def _record_events(self, evtr: EventsToRecord) -> None:
        raise NotImplementedError


@dataclass
class EventStore(AbstractEventStore):
    _path: str
    on_recorded: Callable[[List[Event]], None] = field(default=lambda events: None)

    def __post_init__(self):
        Path(self._path).mkdir(parents=True, exist_ok=True)
        _log.info("Using data directory: %s", Path(self._path).absolute())

    def _record_events(self, evtr: EventsToRecord):
        index = len(list(Path(self._path).glob("*")))
        for e in evtr.events:
            e.version = index
            self._store(e)
            index += 1

    def _load_events(self) -> List[Event]:
        return [self._load(file) for file in sorted(Path(self._path).glob("*"))]

    def _store(self, e: Event) -> None:
        Path(self._path, f"{e.version:05d}.json").write_text(e.json())

    @staticmethod
    def _load(filename: Union[str, Path]) -> Event:
        e_json = json.loads(Path(filename).read_text())

        from food_truck.backend.domain import events

        return getattr(events, e_json.get("type_"))(**e_json)


@dataclass
class DummyEventStore(AbstractEventStore):
    _entries: List[Event] = field(default_factory=list)
    on_recorded: Callable[[List[Event]], None] = field(default=lambda events: None)

    def _record_events(self, evtr: EventsToRecord) -> None:
        index = len(self._entries)
        for e in evtr.events:
            e.version = index
            self._store(e)
            index += 1

    def _load_events(self) -> List[Event]:
        return self._entries

    def _store(self, e: Event) -> None:
        e.version = len(self._entries)
        self._entries.append(e)
