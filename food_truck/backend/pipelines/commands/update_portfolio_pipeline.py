import logging
from dataclasses import dataclass
from typing import Set

from food_truck.backend.domain.events import StockSold, StockBought, StockPriceUpdated
from food_truck.contract.commands import UpdatePortfolio
from food_truck.contract.stock_exchange_provider import AbstractStockExchangeProvider
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
class UpdatePortfolioContextModel(AbstractMessageContextModel):  # noqa Pycharm
    values: Set[str]


class UpdatePortfolioContextManager(AbstractContextManager):
    STREAM = [StockBought, StockSold]

    def __init__(self, es: AbstractEventStore):
        self._symbols: Set[str] = set()
        replay_result = es.replay(self.STREAM)
        self.update(replay_result.events)
        super().__init__(replay_result.version)

    def load(self, message: AbstractMessage) -> UpdatePortfolioContextModel:
        return UpdatePortfolioContextModel(version=self.version, values=self._symbols)

    def _apply(self, e: Event):
        if isinstance(e, StockBought):
            self._symbols.add(e.symbol)
        elif isinstance(e, StockSold):
            self._symbols.remove(e.symbol)


@dataclass
class UpdatePortfolioProcessor(AbstractProcessor):
    _ex: AbstractStockExchangeProvider

    def process(self, cmd: UpdatePortfolio, ctx: UpdatePortfolioContextModel) -> Output:
        current_prices = self._ex.get_price(list(ctx.values))

        events = []
        for symbol, price in current_prices:
            if price == 0.0:
                continue
            events.append(StockPriceUpdated(symbol=symbol, price=price))

        return CommandOutput(
            status=Success(),
            evtr=EventsToRecord(
                version=ctx.version,
                stream=UpdatePortfolioContextManager.STREAM,
                events=events,
            ),
        )
