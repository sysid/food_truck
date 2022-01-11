import abc
from typing import List, Tuple

from pydantic import BaseModel


class CandidateStockInfo(BaseModel):
    name: str
    symbol: str
    currency: str
    price: float


class AbstractStockExchangeProvider(abc.ABC):
    @abc.abstractmethod
    def get_price(self, symbols: List[str]) -> List[Tuple[str, float]]:
        raise NotImplementedError

    @abc.abstractmethod
    def find_candidates(self, pattern: str) -> List[CandidateStockInfo]:
        raise NotImplementedError
