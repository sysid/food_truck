import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

from food_truck.backend.domain.events import StockBought, StockSold
from food_truck.contract.queries import (
    PortfolioStockQuery,
    MatchingStock,
    PortfolioStockQueryResult,
)
from food_truck.backend.eventstore.event_store import AbstractEventStore, Event
from food_truck.backend.pipelines.abstract_pipeline import (
    AbstractContextManager,
    AbstractMessageContextModel,
    QueryOutput,
    AbstractProcessor,
)

_log = logging.getLogger(__name__)

Name = str
Symbol = str


@dataclass
class PortfolioStockQueryContextModel(AbstractMessageContextModel):  # noqa Pycharm
    matching_stocks: List[Tuple[Name, Symbol]]  # noqa E275


class PortfolioStockQueryContextManager(AbstractContextManager):
    STREAM = [StockBought, StockSold]

    def __init__(self, es: AbstractEventStore):
        self._portfolio: Dict[Name, Symbol] = {}
        replay_result = es.replay(self.STREAM)
        self.update(replay_result.events)
        super().__init__(replay_result.version)

    def load(self, message: PortfolioStockQuery) -> PortfolioStockQueryContextModel:
        pattern = message.pattern

        matching_stocks: List[Tuple[Name, Symbol]] = []  # noqa E275
        for symbol, name in self._portfolio.items():
            if pattern in symbol or pattern in name:
                matching_stocks.append((name, symbol))
        return PortfolioStockQueryContextModel(
            version=self.version, matching_stocks=matching_stocks
        )

    def _apply(self, e: Event):
        if isinstance(e, StockBought):
            self._portfolio[e.symbol] = e.name
        elif isinstance(e, StockSold):
            del self._portfolio[e.symbol]


@dataclass
class PortfolioStockQueryProcessor(AbstractProcessor):
    def process(
        self, cmd: PortfolioStockQuery, ctx: PortfolioStockQueryContextModel
    ) -> QueryOutput:
        matching_stocks = []
        for stock in ctx.matching_stocks:
            matching_stocks.append(MatchingStock(name=stock[0], symbol=stock[1]))
        return QueryOutput(
            result=PortfolioStockQueryResult(matching_stocks=matching_stocks)
        )
