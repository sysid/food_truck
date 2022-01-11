from food_truck.backend.eventstore.event_store import Event


# TODO: DI
class StockBought(Event):
    name: str
    symbol: str
    currency: str
    qty: int
    price: float


class StockPriceUpdated(Event):
    symbol: str
    price: float


class StockSold(Event):
    symbol: str


class DummyEvent(Event):
    symbol: str
