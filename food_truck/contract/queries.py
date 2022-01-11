from typing import List

from pydantic import BaseModel

from food_truck.backend.pipelines.message import Query, QueryResult


class CandidateStocksQuery(Query):
    pattern: str


class CandidateStock(BaseModel):
    name: str
    symbol: str
    currency: str
    price: float


class CandidateStocksQueryResult(QueryResult):
    candidates: List[CandidateStock]


class PortfolioQuery(Query):
    pass


class StockInfo(BaseModel):
    name: str
    symbol: str
    currency: str
    qty: int
    buying_price: float
    buying_value: float
    current_price: float
    current_value: float
    return_: float
    rate_of_return: float


class PortfolioQueryResult(QueryResult):
    stocks: List[StockInfo]
    portfolio_value: float
    portfolio_rate_of_return: float


class PortfolioStockQuery(Query):
    pattern: str


class MatchingStock(BaseModel):
    name: str
    symbol: str


class PortfolioStockQueryResult(QueryResult):
    matching_stocks: List[MatchingStock]
