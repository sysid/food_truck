import logging
from dataclasses import dataclass
from typing import Set

from food_truck.backend.domain.events import StockBought, StockSold
from food_truck.contract.commands import SellStock
from food_truck.backend.eventstore.event_store import (
    AbstractEventStore,
    Event,
    EventsToRecord,
)
from food_truck.backend.pipelines.message import AbstractMessage, Success, Failure
from food_truck.backend.pipelines.abstract_pipeline import (
    AbstractContextManager,
    AbstractMessageContextModel,
    Output,
    CommandOutput,
    AbstractProcessor,
)

_log = logging.getLogger(__name__)


@dataclass(kw_only=True)
class SellStockContextModel(AbstractMessageContextModel):  # noqa
    values: Set[str]


class SellStockContextManager(AbstractContextManager):
    STREAM = [StockBought, StockSold]

    def __init__(self, es: AbstractEventStore):
        self._symbols: Set[str] = set()
        replay_result = es.replay(self.STREAM)
        self.update(replay_result.events)
        super().__init__(replay_result.version)

    def load(self, message: SellStock) -> SellStockContextModel:
        return SellStockContextModel(version=self.version, values=self._symbols)

    def _apply(self, e: Event):
        if isinstance(e, StockBought):
            self._symbols.add(e.symbol)
        elif isinstance(e, StockSold):
            self._symbols.remove(e.symbol)
        else:
            _log.debug(f"Unhandled event: {e}")


@dataclass
class SellStockProcessor(AbstractProcessor):
    def process(self, cmd: AbstractMessage, ctx: AbstractMessageContextModel) -> Output:
        assert isinstance(cmd, SellStock)
        assert isinstance(ctx, SellStockContextModel)

        if cmd.symbol in ctx.values:
            return CommandOutput(
                status=Success(),
                evtr=EventsToRecord(
                    version=ctx.version,
                    stream=SellStockContextManager.STREAM,
                    events=[
                        StockSold(
                            symbol=cmd.symbol,
                        )
                    ],
                ),
            )
        return CommandOutput(
            status=Failure(
                error_message=f"Stock '{cmd.symbol}' not in portfolio. It cannot be sold!"
            ),
        )
