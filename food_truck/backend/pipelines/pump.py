import abc
import logging
from dataclasses import dataclass, field
from typing import Type, Dict, List, Callable

from food_truck.backend.eventstore.event_store import (
    Event,
    EventStore,
    AbstractEventStore,
)
from food_truck.backend.pipelines.message import AbstractMessage, NoResponse
from food_truck.backend.pipelines.abstract_pipeline import (
    AbstractMessageContextModel,
    AbstractContextManager,
    Output,
    CommandOutput,
    QueryOutput,
    NotificationOutput,
    AbstractProcessor,
)

_log = logging.getLogger(__name__)


@dataclass
class Pipeline:
    load_context: Callable[[AbstractMessage], AbstractMessageContextModel]
    process: Callable[[AbstractMessage, AbstractMessageContextModel], Output]
    update_context: Callable[[List[Event]], None]


class AbstractPump(abc.ABC):
    _message_pipeline_directory: Dict[Type, Pipeline]
    _es: EventStore

    @abc.abstractmethod
    def register(
        self,
        msg: AbstractMessage,
        ctx_mgr: AbstractContextManager,
        processor: AbstractProcessor,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def handle(self, msg: AbstractMessage) -> AbstractMessage:
        raise NotImplementedError


@dataclass
class Pump(AbstractPump):
    _es: AbstractEventStore
    _message_pipeline_directory: Dict[Type, Pipeline] = field(default_factory=dict)

    def register(
        self,
        msg_type: Type[AbstractMessage],
        ctx_mgr: AbstractContextManager,
        processor: AbstractProcessor,
    ) -> None:
        """register message handler pipeline"""
        self._message_pipeline_directory[msg_type] = Pipeline(
            load_context=ctx_mgr.load,
            process=processor.process,
            update_context=ctx_mgr.update,
        )

    def handle(self, msg: AbstractMessage) -> AbstractMessage:
        """https://danielwhittaker.me/2020/02/20/cqrs-step-step-guide-flow-typical-application/"""
        _log.debug(f"{msg.__module__}.{msg.__class__.__qualname__}: [{msg}]")

        try:
            pipeline = self._message_pipeline_directory[type(msg)]
            ctx = pipeline.load_context(
                msg
            )  # 3. The handler prepares the model/aggregate root
            out = pipeline.process(
                msg, ctx
            )  # 4. The command is issued / 5. The command handler requests the changes (out)
            return self._dispatch(out)  # 6. storing / 7 events published onto bus
        except KeyError as e:
            _log.error("Unable to handle event: %s. Unknown type.", type(msg))
            return NoResponse()

    def _dispatch(self, output: Output) -> AbstractMessage:
        """dispatch the handler result"""
        if isinstance(output, CommandOutput):
            if output.evtr is not None:
                self._es.record(evtr=output.evtr)  # TODO: Failure?
                self._update_contexts(output.evtr.events)  # updates in-mem projection
            return output.status
        elif isinstance(output, QueryOutput):
            return output.result
        elif isinstance(output, NotificationOutput):
            for cmd in output.commands:
                self.handle(cmd)
            return NoResponse()

    def _update_contexts(self, events: List[Event]):
        """update model contexts of interested handler"""
        context_updaters = [
            pipeline.update_context
            for pipeline in self._message_pipeline_directory.values()
        ]
        for update in context_updaters:
            _log.debug("Updating context: %s", update)
            update(events)
