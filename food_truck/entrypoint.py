import logging

from food_truck.backend.adapter.alpha_vantage_provider import AlphaVantageProvider
from food_truck.backend.adapter.stock_exchange_provider import StockExchangeProvider
from food_truck.backend.eventstore.event_store import EventStore
from food_truck.backend.pipelines.commands.buy_stock_pipeline import (
    BuyStockContextManager,
    BuyStockProcessor,
)
from food_truck.backend.pipelines.commands.sell_stock_pipeline import (
    SellStockContextManager,
    SellStockProcessor,
)
from food_truck.backend.pipelines.commands.update_portfolio_pipeline import (
    UpdatePortfolioContextManager,
    UpdatePortfolioProcessor,
)
from food_truck.backend.pipelines.queries.candidate_stocks_pipeline import (
    CandidateStocksQueryContextManager,
    CandidateStocksQueryProcessor,
)
from food_truck.backend.pipelines.queries.portfolio_pipeline import (
    PortfolioQueryContextManager,
    PortfolioQueryProcessor,
)
from food_truck.backend.pipelines.queries.portfolio_stock_pipeline import (
    PortfolioStockQueryContextManager,
    PortfolioStockQueryProcessor,
)
from food_truck.contract.commands import BuyStock, SellStock, UpdatePortfolio
from food_truck.contract.queries import (
    CandidateStocksQuery,
    PortfolioQuery,
    PortfolioStockQuery,
    PortfolioQueryResult,
    CandidateStocksQueryResult,
    PortfolioStockQueryResult,
)
from food_truck.environment import config
from food_truck.frontend.user_interface import UserInterface
from food_truck.backend.pipelines.abstract_pipeline import (
    AbstractContextManager,
    AbstractProcessor,
)
from food_truck.backend.pipelines.pump import Pump

_log = logging.getLogger(__name__)
log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=log_fmt, level=config.log_level, datefmt=datefmt)

ex = StockExchangeProvider(
    _av=AlphaVantageProvider(
        _base_url=config.alpha_vantage_url, _api_key=config.alpha_vantage_apikey
    )
)
es = EventStore("eventstore.db")
pump = Pump(_es=es)
mcm: AbstractContextManager
mp: AbstractProcessor

pump.register(BuyStock, BuyStockContextManager(es=es), BuyStockProcessor())
pump.register(SellStock, SellStockContextManager(es=es), SellStockProcessor())
pump.register(
    UpdatePortfolio,
    UpdatePortfolioContextManager(es=es),
    UpdatePortfolioProcessor(_ex=ex),
)

pump.register(
    CandidateStocksQuery,
    CandidateStocksQueryContextManager(es=es),
    CandidateStocksQueryProcessor(_ex=ex),
)
pump.register(
    PortfolioQuery, PortfolioQueryContextManager(es=es), PortfolioQueryProcessor()
)
pump.register(
    PortfolioStockQuery,
    PortfolioStockQueryContextManager(es=es),
    PortfolioStockQueryProcessor(),
)

frontend = UserInterface()


def on_portfolio_query(q: PortfolioQuery) -> None:
    pofo = pump.handle(q)
    assert isinstance(pofo, PortfolioQueryResult)
    frontend.display(pofo=pofo)


def on_update_portfolio_command(c: UpdatePortfolio) -> None:
    pump.handle(c)
    pofo = pump.handle(PortfolioQuery())
    assert isinstance(pofo, PortfolioQueryResult)
    frontend.display(pofo=pofo)


def on_candidate_stocks_query(q: CandidateStocksQuery) -> None:
    candidates = pump.handle(q)
    assert isinstance(candidates, CandidateStocksQueryResult)

    if cmd := frontend.select_stock_to_buy(candidates=candidates.candidates):
        pump.handle(cmd)
        frontend.display_buy_confirmation(
            symbol=cmd.symbol, qty=cmd.qty, price=cmd.price
        )


def on_portfolio_stock_query(q: PortfolioStockQuery) -> None:
    stocks = pump.handle(q)
    assert isinstance(stocks, PortfolioStockQueryResult)

    if cmd := frontend.select_stock_to_sell(candidates=stocks):
        pump.handle(cmd)
        frontend.display_sell_confirmation(symbol=cmd.symbol)


frontend.on_portfolio_query = on_portfolio_query
frontend.on_portfolio_stock_query = on_portfolio_stock_query
frontend.on_candidate_stock_query = on_candidate_stocks_query
frontend.on_update_portfolio_command = on_update_portfolio_command

_log.debug(config.log_config())

frontend.run()
