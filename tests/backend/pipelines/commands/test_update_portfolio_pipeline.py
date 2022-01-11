from food_truck.backend.adapter.alpha_vantage_provider import AlphaVantageProvider
from food_truck.backend.adapter.stock_exchange_provider import StockExchangeProvider
from food_truck.backend.eventstore.event_store import EventStore
from food_truck.backend.pipelines.commands.update_portfolio_pipeline import (
    UpdatePortfolioContextManager,
    UpdatePortfolioProcessor,
)
from food_truck.contract.commands import UpdatePortfolio
from food_truck.environment import config
from food_truck.backend.pipelines.message import Success
from food_truck.backend.pipelines.pump import Pump


def test_sell_existing_stock():
    # given prod setup
    ex = StockExchangeProvider(
        _av=AlphaVantageProvider(
            _base_url=config.alpha_vantage_url, _api_key=config.alpha_vantage_apikey
        )
    )
    es = EventStore("eventstore.db")
    pump = Pump(_es=es)

    pump.register(
        UpdatePortfolio,
        UpdatePortfolioContextManager(es=es),
        processor=UpdatePortfolioProcessor(_ex=ex),
    )

    # when command is processed
    msg = UpdatePortfolio()
    result = pump.handle(msg)
    result = pump.handle(msg)

    # then:
    assert isinstance(result, Success)
