from pathlib import Path
from typing import List

import pytest

from food_truck.backend.domain.events import DummyEvent, StockBought, StockPriceUpdated
from food_truck.backend.eventstore.event_store import (
    EventStore,
    EventsToRecord,
    StreamVersionError,
    Event,
    DummyEventStore,
)


@pytest.fixture()
def evtr():
    return EventsToRecord(version=0, stream=None, events=[DummyEvent(symbol="x")])


class TestEventStore:
    def test_record(self, tmpdir):
        # given: Event which has not been persisted
        filename = f"{tmpdir}/00000.json"
        Path(filename).unlink(missing_ok=True)

        # when: event is recorded
        es = EventStore(_path=tmpdir)
        es.record(
            evtr=EventsToRecord(version=0, stream=None, events=[DummyEvent(symbol="x")])
        )

        # then persisted event exists
        assert Path(filename).exists()

    def test_version_check(self, tmpdir, evtr):
        # when: event is recorded with wrong version
        evtr.version = 1
        es = EventStore(_path=tmpdir)
        with pytest.raises(StreamVersionError):
            es.record(evtr=evtr)

    def test_on_recorded(self, tmpdir, evtr):
        # given
        def on_recorded(events: List[Event]) -> None:
            print(*events)
            Path(tmpdir, "on_recorded").touch()

        # when: event is recorded
        es = EventStore(_path=tmpdir, on_recorded=on_recorded)
        es.record(evtr)

        # then the sentinel file is created via on_recorded
        assert Path(tmpdir, "on_recorded").exists()

    def test_replay(self, tmpdir):
        evtr = EventsToRecord(
            version=0, stream=None, events=[DummyEvent(symbol="x"), Event()]
        )

        es = EventStore(_path=tmpdir)
        es.record(evtr=evtr)

        replay_result = es.replay()
        events = replay_result.events
        assert isinstance(events[0], DummyEvent)
        assert isinstance(events[1], Event)
        assert len(events) == 2

        replay_result = es.replay(stream=[DummyEvent])
        events = replay_result.events
        assert isinstance(events[0], DummyEvent)
        assert len(events) == 1

    def test__store__load(self, tmpdir):
        # given: Event which has not been persisted
        filename = f"{tmpdir}/00000.json"
        Path(filename).unlink(missing_ok=True)
        e = DummyEvent(symbol="x")

        # when: event is stored
        es = EventStore(_path=tmpdir)
        es._store(e)

        # then: persisted event exists
        assert Path(filename).exists()

        # when persisted event is re-loaded
        restored_event = es._load(filename)

        # then: restore event is identical to original
        assert e == restored_event
        assert restored_event.type_ == restored_event.__class__.__name__ == "DummyEvent"

    def test_event_versioning(self):
        evtr = EventsToRecord(
            version=0,
            stream=None,
            events=[
                StockBought(
                    name="Microsoft",
                    symbol="MSFT",
                    currency="USD",
                    qty=10,
                    price=300.0,
                ),
                StockPriceUpdated(
                    symbol="MSFT",
                    price=301.0,
                ),
                StockPriceUpdated(
                    symbol="MSFT",
                    price=302.0,
                ),
                StockBought(
                    name="Apple",
                    symbol="AAA",
                    currency="USD",
                    qty=10,
                    price=10.0,
                ),
                StockBought(
                    name="Bayerische Motorenwerke",
                    symbol="BMW",
                    currency="EUR",
                    qty=10,
                    price=2000.0,
                ),
                StockPriceUpdated(
                    symbol="BMW",
                    price=2001.0,
                ),
            ],
        )
        es = DummyEventStore()
        es.record(evtr=evtr)
        assert es._entries[-1].version == 5


class TestDummyEventStore:
    def test_record_restore(self):
        evtr = EventsToRecord(
            version=0,
            stream=None,
            events=[
                StockBought(
                    name="Microsoft",
                    symbol="MSFT",
                    currency="USD",
                    qty=10,
                    price=300.0,
                ),
                StockPriceUpdated(
                    symbol="MSFT",
                    price=300.0,
                ),
            ],
        )
        es = DummyEventStore()
        es.record(evtr=evtr)

        assert es._entries[1].version == 1

        replay_result = es.replay()
        assert len(replay_result.events) == 2

        replay_result = es.replay(stream=[StockBought])
        assert len(replay_result.events) == 1

        replay_result = es.replay(stream=[StockBought, StockPriceUpdated])
        assert len(replay_result.events) == 2
