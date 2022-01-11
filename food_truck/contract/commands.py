from datetime import datetime

from food_truck.backend.pipelines.message import Command


class BuyStock(Command):
    name: str
    symbol: str
    currency: str
    qty: int
    price: float
    bought: datetime


class SellStock(Command):
    symbol: str


class UpdatePortfolio(Command):
    pass


class DummyCommand(Command):
    symbol: str
