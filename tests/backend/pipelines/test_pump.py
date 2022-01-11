from food_truck.backend.domain.events import DummyEvent
from food_truck.backend.eventstore.event_store import DummyEventStore
from food_truck.backend.pipelines.commands.dummy_pipeline import (
    DummyContextManager,
    DummyProcessor,
)
from food_truck.contract.commands import DummyCommand
from food_truck.backend.pipelines.pump import Pump


def test_pump(tmpdir):
    es = DummyEventStore()
    ctx_mgr = DummyContextManager(es=es)

    p = Pump(
        _es=es,
    )
    p.register(DummyCommand, ctx_mgr, DummyProcessor())
    p.handle(DummyCommand(symbol="x"))

    assert ctx_mgr._symbols == {"x"}
    assert isinstance(es._entries[0], DummyEvent)
