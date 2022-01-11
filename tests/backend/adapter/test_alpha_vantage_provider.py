import pytest

from food_truck.backend.adapter.alpha_vantage_provider import AlphaVantageProvider
from food_truck.environment import config


@pytest.mark.integtest
def test_get_quote():
    p = AlphaVantageProvider(
        _base_url=config.alpha_vantage_url, _api_key=config.alpha_vantage_apikey
    )
    stock_price = p.get_quote("MSFT")
    assert stock_price.id_ == "MSFT"
    assert isinstance(stock_price.price, float)


def test_get_empty_quote():
    p = AlphaVantageProvider(
        _base_url=config.alpha_vantage_url, _api_key=config.alpha_vantage_apikey
    )
    stock_price = p.get_quote("BMW")
    assert stock_price.id_ == "BMW"
    assert stock_price.price == 0.0


def test_get_conversion_rate():
    p = AlphaVantageProvider(
        _base_url=config.alpha_vantage_url, _api_key=config.alpha_vantage_apikey
    )
    er = p.get_conversion_rate("AED")
    assert er.from_currency == "AED"
    assert er.rate < 1
    _ = None


def test_find_matching_stocks():
    p = AlphaVantageProvider(
        _base_url=config.alpha_vantage_url, _api_key=config.alpha_vantage_apikey
    )
    ms = p.find_matching_stocks("MSFT")
    assert len(ms) >= 2

    msft_stock_info = ms[0]
    assert msft_stock_info.symbol == "MSFT"
