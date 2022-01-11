import logging
from dataclasses import dataclass
from typing import Set

from food_truck.backend.domain.events import DummyEvent
from food_truck.contract.commands import DummyCommand
from food_truck.backend.eventstore.event_store import (
    AbstractEventStore,
    Event,
    EventsToRecord,
)
from food_truck.backend.pipelines.message import AbstractMessage, Success
from food_truck.backend.pipelines.abstract_pipeline import (
    AbstractContextManager,
    AbstractMessageContextModel,
    Output,
    CommandOutput,
    AbstractProcessor,
)

_log = logging.getLogger(__name__)


@dataclass
class DummyContextModel(AbstractMessageContextModel):  # noqa Pycharm
    values: Set[str]


class DummyContextManager(AbstractContextManager):
    STREAM = [DummyEvent]

    def __init__(self, es: AbstractEventStore):
        self._symbols: Set[str] = set()
        replay_result = es.replay(self.STREAM)
        self.update(replay_result.events)
        super().__init__(replay_result.version)

    def load(self, message: AbstractMessage) -> DummyContextModel:
        return DummyContextModel(version=self.version, values=self._symbols)

    def _apply(self, e: Event):
        if isinstance(e, DummyEvent):
            self._symbols.add(e.symbol)


@dataclass
class DummyProcessor(AbstractProcessor):
    def process(self, cmd: DummyCommand, ctx: DummyContextModel) -> Output:
        _log.info("Run! Stock: %s", cmd.symbol)
        return CommandOutput(
            status=Success(),
            evtr=EventsToRecord(
                version=ctx.version,
                stream=DummyContextManager.STREAM,
                events=[
                    DummyEvent(
                        symbol=cmd.symbol,
                    ),
                ],
            ),
        )
