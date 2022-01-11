import logging
from dataclasses import dataclass

from food_truck.backend.domain.events import StockBought, StockPriceUpdated
from food_truck.contract.commands import BuyStock
from food_truck.backend.eventstore.event_store import (
    AbstractEventStore,
    Event,
    EventsToRecord,
)
from food_truck.backend.pipelines.message import AbstractMessage, Success
from food_truck.backend.pipelines.abstract_pipeline import (
    AbstractContextManager,
    AbstractMessageContextModel,
    Output,
    CommandOutput,
    AbstractProcessor,
)

_log = logging.getLogger(__name__)


@dataclass
class BuyStockContextModel(AbstractMessageContextModel):
    pass


class BuyStockContextManager(AbstractContextManager):
    STREAM = []

    def __init__(self, es: AbstractEventStore):
        super().__init__()

    def load(self, message: AbstractMessage) -> BuyStockContextModel:
        return BuyStockContextModel()

    def _apply(self, event: Event):
        pass


@dataclass
class BuyStockProcessor(AbstractProcessor):
    def process(self, cmd: BuyStock, ctx: BuyStockContextModel) -> Output:
        _log.info("Issuing events: StockBought, StockPriceUpdated")
        return CommandOutput(
            status=Success(),
            evtr=EventsToRecord(
                version=ctx.version,
                stream=BuyStockContextManager.STREAM,
                events=[
                    StockBought(
                        name=cmd.name,
                        symbol=cmd.symbol,
                        currency=cmd.currency,
                        qty=cmd.qty,
                        price=cmd.price,
                    ),
                    StockPriceUpdated(
                        symbol=cmd.symbol,
                        price=cmd.price,
                    ),
                ],
            ),
        )
