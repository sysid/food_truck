import logging
from dataclasses import dataclass

from food_truck.backend.eventstore.event_store import AbstractEventStore, Event
from food_truck.contract.commands import DummyCommand
from food_truck.contract.notifications import DummyNotification
from food_truck.backend.pipelines.message import AbstractMessage
from food_truck.backend.pipelines.abstract_pipeline import (
    AbstractContextManager,
    AbstractMessageContextModel,
    Output,
    NotificationOutput,
    AbstractProcessor,
)

_log = logging.getLogger(__name__)


@dataclass
class DummyContextModel(AbstractMessageContextModel):  # noqa Pycharm
    pass


class DummyContextManager(AbstractContextManager):
    STREAM = []

    def __init__(self, es: AbstractEventStore):
        replay_result = es.replay(self.STREAM)
        self.update(replay_result.events)
        super().__init__(replay_result.version)

    def load(self, message: AbstractMessage) -> DummyContextModel:
        return DummyContextModel(version=self.version)

    def _apply(self, e: Event):
        pass


@dataclass
class DummyProcessor(AbstractProcessor):
    def process(self, n: DummyNotification, ctx: DummyContextModel) -> Output:
        _log.info(n)
        return NotificationOutput(commands=[DummyCommand(symbol="DUMMY_STOCK")])
