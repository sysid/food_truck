import logging

from food_truck.backend.pipelines.commands.dummy_pipeline import (
    DummyContextManager as DummyCommandContextManager,
    DummyProcessor as DummyCommandProcessor,
)
from food_truck.backend.pipelines.notifications.dummy_pipeline import (
    DummyContextManager as DummyNotificationContextManager,
    DummyProcessor as DummyNotificationProcessor,
)
from food_truck.contract.commands import DummyCommand
from food_truck.contract.notifications import DummyNotification
from food_truck.backend.pipelines.message import NoResponse
from food_truck.backend.pipelines.pump import Pump


def test_sell_existing_stock(eventstore, caplog):
    caplog.set_level(logging.DEBUG)

    # given pipeline
    pump = Pump(_es=eventstore)
    pump.register(
        DummyNotification,
        DummyNotificationContextManager(es=eventstore),
        processor=DummyNotificationProcessor(),
    )
    pump.register(
        DummyCommand,
        DummyCommandContextManager(es=eventstore),
        processor=DummyCommandProcessor(),
    )

    # when notification is processed
    msg = DummyNotification()
    result = pump.handle(msg)

    # then:
    assert isinstance(result, NoResponse)

    # then: the triggered command gets dispatched
    assert "DUMMY_STOCK" in caplog.text
