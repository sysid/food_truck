from dataclasses import dataclass
from datetime import datetime
from typing import Sequence, Dict

from pydantic import BaseModel

from food_truck.backend.domain.events import StockPriceUpdated, StockSold, StockBought
from food_truck.backend.domain.portfolio import Stock, Portfolio
from food_truck.contract.queries import PortfolioQuery, PortfolioQueryResult, StockInfo
from food_truck.backend.eventstore.event_store import AbstractEventStore, Event
from food_truck.backend.pipelines.message import AbstractMessage
from food_truck.backend.pipelines.abstract_pipeline import (
    AbstractContextManager,
    AbstractMessageContextModel,
    QueryOutput,
    AbstractProcessor,
)


class PortfolioQueryStockInfo(BaseModel):
    name: str
    symbol: str
    currency: str
    qty: int
    buying_price: float
    bought: datetime
    current_price: float
    last_updated: datetime


@dataclass(kw_only=True)
class PortfolioQueryContextModel(AbstractMessageContextModel):  # noqa Pycharm
    entries: Sequence[PortfolioQueryStockInfo]


class PortfolioQueryContextManager(AbstractContextManager):
    STREAM = [StockBought, StockSold, StockPriceUpdated]

    def __init__(self, es: AbstractEventStore):
        self._portfolio: Dict[str, PortfolioQueryStockInfo] = {}
        replay_result = es.replay(self.STREAM)
        self.update(replay_result.events)
        super().__init__(replay_result.version)

    def load(self, message: AbstractMessage) -> PortfolioQueryContextModel:
        """context loader"""
        return PortfolioQueryContextModel(
            version=self.version, entries=list(self._portfolio.values())
        )

    def _apply(self, e: Event) -> None:
        if isinstance(e, StockBought):
            if (stockinfo := self._portfolio.get(e.symbol)) is not None:
                stockinfo.qty += e.qty
                stockinfo.buying_price = (
                    stockinfo.buying_price + e.price
                ) / 2  # unreal averaging simplification
            else:
                stockinfo = PortfolioQueryStockInfo(
                    name=e.name,
                    symbol=e.symbol,
                    currency=e.currency,
                    qty=e.qty,
                    buying_price=e.price,
                    bought=e.created_at,
                    current_price=e.price,
                    last_updated=e.created_at,
                )
                self._portfolio[e.symbol] = stockinfo
        elif isinstance(e, StockSold):
            self._portfolio.pop(e.symbol)
        elif isinstance(e, StockPriceUpdated):
            stockinfo = self._portfolio.get(e.symbol)
            stockinfo.current_price = e.price
            stockinfo.last_updated = e.created_at


@dataclass
class PortfolioQueryProcessor(AbstractProcessor):
    def process(
        self, cmd: PortfolioQuery, ctx: PortfolioQueryContextModel
    ) -> QueryOutput:
        pofo = Portfolio(
            entries=[
                Stock(
                    name=stockinfo.name,
                    symbol=stockinfo.symbol,
                    currency=stockinfo.currency,
                    qty=stockinfo.qty,
                    buying_price=stockinfo.buying_price,
                    bought=stockinfo.bought,
                    current_price=stockinfo.current_price,
                    last_updated=stockinfo.last_updated,
                )
                for stockinfo in ctx.entries
            ]
        )
        returns = pofo.calculate_returns()

        result = PortfolioQueryResult(
            stocks=[
                StockInfo(
                    name=stock.name,
                    symbol=stock.symbol,
                    currency=stock.currency,
                    qty=stock.qty,
                    buying_price=stock.buying_price,
                    buying_value=stock.qty * stock.buying_price,
                    current_price=stock.current_price,
                    current_value=stock.qty * stock.current_price,
                    return_=returns.returns[stock.symbol].return_,
                    rate_of_return=returns.returns[stock.symbol].rate_of_return,
                )
                for stock in pofo.entries
            ],
            portfolio_value=sum(
                [stock.qty * stock.current_price for stock in pofo.entries]
            ),
            portfolio_rate_of_return=returns.total_rate_of_return,
        )
        return QueryOutput(result=result)
