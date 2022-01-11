from dataclasses import dataclass

from food_truck.contract.queries import (
    CandidateStocksQuery,
    CandidateStock,
    CandidateStocksQueryResult,
)
from food_truck.contract.stock_exchange_provider import AbstractStockExchangeProvider
from food_truck.backend.eventstore.event_store import AbstractEventStore, Event
from food_truck.backend.pipelines.message import AbstractMessage
from food_truck.backend.pipelines.abstract_pipeline import (
    AbstractContextManager,
    AbstractMessageContextModel,
    QueryOutput,
    AbstractProcessor,
)


@dataclass
class CandidateStocksQueryContextModel(AbstractMessageContextModel):
    pass


class CandidateStocksQueryContextManager(AbstractContextManager):
    def __init__(self, es: AbstractEventStore):
        super().__init__()

    def load(self, message: AbstractMessage) -> CandidateStocksQueryContextModel:
        return CandidateStocksQueryContextModel()

    def _apply(self, event: Event):
        pass


@dataclass
class CandidateStocksQueryProcessor(AbstractProcessor):
    _ex: AbstractStockExchangeProvider

    def process(
        self, cmd: CandidateStocksQuery, ctx: CandidateStocksQueryContextModel
    ) -> QueryOutput:
        assert isinstance(cmd, CandidateStocksQuery)
        assert isinstance(ctx, CandidateStocksQueryContextModel)

        candidates = self._ex.find_candidates(cmd.pattern)
        candidate_stocks = []
        for candidate in candidates:
            candidate_stocks.append(
                CandidateStock(
                    name=candidate.name,
                    symbol=candidate.symbol,
                    currency=candidate.currency,
                    price=candidate.price,
                )
            )

        return QueryOutput(
            result=CandidateStocksQueryResult(candidates=candidate_stocks)
        )
