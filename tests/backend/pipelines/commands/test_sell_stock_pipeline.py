from food_truck.backend.domain.events import StockSold
from food_truck.backend.pipelines.commands.sell_stock_pipeline import (
    SellStockContextManager,
    SellStockContextModel,
    SellStockProcessor,
)
from food_truck.contract.commands import SellStock
from food_truck.backend.pipelines.message import Failure, Success
from food_truck.backend.pipelines.pump import Pump


def test_sell_existing_stock(eventstore):
    # given pipeline
    pump = Pump(_es=eventstore)
    pump.register(
        SellStock,
        SellStockContextManager(es=eventstore),
        processor=SellStockProcessor(),
    )

    # when command is processed
    msg = SellStock(symbol="AAA")
    result = pump.handle(msg)

    # then:
    assert isinstance(result, Success)

    # then: event is appended in ES
    event = eventstore._entries[-1]
    assert event.version == 6
    assert isinstance(event, StockSold)

    # then: in-mem model is updated
    updated_model = pump._message_pipeline_directory[SellStock].load_context(msg)
    assert isinstance(updated_model, SellStockContextModel)
    assert updated_model.values == {"MSFT", "BMW"}
    assert updated_model.version == 6


def test_sell_non_existing_stock(eventstore):
    # given
    pump = Pump(_es=eventstore)
    pump.register(
        SellStock,
        SellStockContextManager(es=eventstore),
        processor=SellStockProcessor(),
    )

    # when command is processed
    msg = SellStock(symbol="BBB")
    result = pump.handle(msg)

    # then:
    assert isinstance(result, Failure)

    # then: event is NOT appended in ES
    event = eventstore._entries[-1]
    assert event.version == 5

    # then: in-mem model is NOT updated
    updated_model = pump._message_pipeline_directory[SellStock].load_context(msg)
    assert isinstance(updated_model, SellStockContextModel)
    assert updated_model.values == {"AAA", "MSFT", "BMW"}
    assert updated_model.version == 4
