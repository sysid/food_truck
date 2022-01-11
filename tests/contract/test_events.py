from food_truck.contract.queries import PortfolioStockQueryResult, MatchingStock


def test_portfolio_stock_result():
    result = PortfolioStockQueryResult(
        matching_stocks=[MatchingStock(name="Microsoft", symbol="MSFT")]
    )
    print(result)
