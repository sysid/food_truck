from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict

from pydantic import BaseModel


class Stock(BaseModel):
    name: str
    symbol: str
    currency: str
    qty: int
    buying_price: float
    bought: date
    current_price: float
    last_updated: date


@dataclass
class EntryReturn:
    return_: float
    rate_of_return: float


@dataclass
class PortfolioReturns:
    total_return: float = 0
    total_rate_of_return: float = 0
    returns: Dict[str, EntryReturn] = field(default_factory=dict)


@dataclass
class Portfolio:
    entries: List[Stock] = field(default_factory=list)

    def calculate_returns(self) -> PortfolioReturns:
        pr = PortfolioReturns()

        for stock in self.entries:
            buying_value = stock.qty * stock.buying_price

            pr.returns[stock.symbol] = EntryReturn(
                return_=stock.qty * stock.current_price - buying_value,
                rate_of_return=(stock.qty * stock.current_price - buying_value)
                / stock.buying_price,
            )

        pr.total_return = sum([r.return_ for r in pr.returns.values()])
        total_buying_value = sum(
            [stock.qty * stock.buying_price for stock in self.entries]
        )
        try:
            pr.total_rate_of_return = pr.total_return / total_buying_value
        except ZeroDivisionError:
            pr.total_rate_of_return = 0

        return pr


@dataclass
class PortfolioManager:  # todo: Why stateless class?
    entries: List[Stock] = field(default_factory=list)
