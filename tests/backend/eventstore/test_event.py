import json
from pathlib import Path

from food_truck.backend.domain.events import DummyEvent


def test_event_serialize_deserialize():
    e = DummyEvent(symbol="x")
    assert e.type_ == e.__class__.__name__ == "DummyEvent"

    Path("/tmp/event.json").write_text(e.json())

    e_json = json.loads(Path("/tmp/event.json").read_text())

    from food_truck.backend.domain import events

    event_type = getattr(events, e_json.get("type_"))
    restored_event = event_type.parse_file("/tmp/event.json")
    assert e == restored_event
    assert restored_event.type_ == restored_event.__class__.__name__ == "DummyEvent"
