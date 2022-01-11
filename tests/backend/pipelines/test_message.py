from food_truck.backend.pipelines.message import Query, AbstractMessage, Request


def test_xxx():
    q = Query()
    assert isinstance(q, AbstractMessage)
    assert issubclass(type(q), Request)
