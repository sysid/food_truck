import logging
from dataclasses import dataclass
from typing import List, Optional

import httpx

_log = logging.getLogger(__name__)


@dataclass
class StockPrice:
    id_: str
    price: float


@dataclass
class StockInfo:
    symbol: str
    name: str
    region: str
    currency: str


@dataclass
class ExchangeRateToEuro:
    from_currency: str
    rate: float


@dataclass
class AlphaVantageProvider:
    """
    https://www.alphavantage.co/documentation/
    """

    _base_url: str
    _api_key: str

    def __post_init__(self):
        self._base_url = f"{self._base_url}/query?apikey={self._api_key}"

    def get_quote(self, symbol: str) -> Optional[StockPrice]:
        endpoint_url = f"{self._base_url}&function=GLOBAL_QUOTE&symbol={symbol}"
        quote = httpx.get(endpoint_url).json()
        if quote and len(quote.get("Global Quote", {})) == 0:
            _log.warning("No quote for %s, returning 0.", symbol)
            id_ = symbol
            price = 0.0
        else:
            id_ = quote.get("Global Quote").get("01. symbol")
            price = float(quote.get("Global Quote").get("05. price"))

        return StockPrice(
            id_=id_,
            price=price,
        )

    def get_conversion_rate(
            self, from_currency: str, to_currency: str = "EUR"
    ) -> ExchangeRateToEuro:
        endpoint_url = f"{self._base_url}/&function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency}&to_currency={to_currency}"
        quote = httpx.get(endpoint_url).json()
        # return ExchangeRateToEuro(
        #     from_currency=from_currency,
        #     rate=float(
        #         quote.get("Realtime Currency Exchange Rate").get("5. Exchange Rate")
        #     ),
        # )
        return ExchangeRateToEuro(
            from_currency=from_currency,
            rate=1.0  # hard-coded due to change in alphavantage API (premium abo needed)
        )

    def find_matching_stocks(self, pattern: str) -> List[StockInfo]:

        try:
            endpoint_url = f"{self._base_url}&function=SYMBOL_SEARCH&keywords={pattern}"
            matching_stocks = httpx.get(endpoint_url).json().get("bestMatches")
        except Exception as e:
            _log.exception(e, stack_info=True)
            matching_stocks = {}

        stock_infos: List[StockInfo] = []
        for ms in matching_stocks:
            stock_infos.append(
                StockInfo(
                    symbol=ms.get("1. symbol"),
                    name=ms.get("2. name"),
                    region=ms.get("4. region"),
                    currency=ms.get("8. currency"),
                )
            )
        return stock_infos
