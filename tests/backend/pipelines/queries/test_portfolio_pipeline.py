from food_truck.backend.pipelines.queries.portfolio_pipeline import (
    PortfolioQueryContextManager,
    PortfolioQueryProcessor,
)
from food_truck.contract.queries import PortfolioQuery, PortfolioQueryResult
from food_truck.backend.pipelines.pump import Pump


def test_load_portfolio(eventstore):
    # given pipeline
    pump = Pump(_es=eventstore)
    pump.register(
        PortfolioQuery,
        PortfolioQueryContextManager(es=eventstore),
        processor=PortfolioQueryProcessor(),
    )

    msg = PortfolioQuery()
    result = pump.handle(msg)

    assert isinstance(result, PortfolioQueryResult)
    assert result.stocks[0].symbol == "MSFT"
    assert result.stocks[0].current_price == 302.0
