import logging
from dataclasses import dataclass
from typing import List, Tuple

from food_truck.backend.adapter.alpha_vantage_provider import (
    AlphaVantageProvider,
    StockPrice,
)
from food_truck.contract.stock_exchange_provider import (
    AbstractStockExchangeProvider,
    CandidateStockInfo,
)

_log = logging.getLogger(__name__)


@dataclass
class StockExchangeProvider(AbstractStockExchangeProvider):
    _av: AlphaVantageProvider

    def get_price(self, symbols: List[str]) -> List[Tuple[str, float]]:
        prices = []
        for symbol in symbols:
            try:
                quote = self._av.get_quote(symbol=symbol)
                prices.append((symbol, quote.price))
            except Exception:
                raise  # todo: needs implementation
        return prices

    def find_candidates(self, pattern: str) -> List[CandidateStockInfo]:
        stock_infos = self._av.find_matching_stocks(pattern)
        candidates = []
        for si in stock_infos:
            try:
                stock_price = self._av.get_quote(si.symbol)
            except Exception as e:
                _log.exception(e, stack_info=True)
                stock_price = StockPrice(id_=si.symbol, price=0)

            candidates.append(
                CandidateStockInfo(
                    name=si.name,
                    symbol=si.symbol,
                    currency=si.currency,
                    price=stock_price.price,
                )
            )
            return candidates
