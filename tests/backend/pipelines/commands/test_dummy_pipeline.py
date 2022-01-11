from food_truck.backend.domain.events import DummyEvent
from food_truck.backend.pipelines.commands.dummy_pipeline import DummyContextManager, DummyProcessor
from food_truck.backend.pipelines.message import Success
from food_truck.backend.pipelines.pump import Pump
from food_truck.contract.commands import DummyCommand


def test_sell_existing_stock(eventstore):
    # given pipeline
    pump = Pump(_es=eventstore)
    pump.register(
        DummyCommand,
        DummyContextManager(es=eventstore),
        processor=DummyProcessor(),
    )

    # when command is processed
    msg = DummyCommand(symbol="AAA")
    result = pump.handle(msg)

    # then:
    assert isinstance(result, Success)

    # then: event is appended in ES
    event = eventstore._entries[-1]
    assert event.version == 6
    assert isinstance(event, DummyEvent)
