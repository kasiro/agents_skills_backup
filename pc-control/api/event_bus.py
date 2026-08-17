# core/event_bus.py
import asyncio
from typing import Dict, Any, Callable, Awaitable, List, Optional
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """
    Простая асинхронная шина событий с хранилищем состояний.
    Позволяет подписываться на события и получать уведомления.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}
        self._context: Dict[str, Any] = {}

    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Подписка на {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable):
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            logger.debug(f"Отписка от {event_type}")

    async def publish(self, event_type: str, data: Dict[str, Any]):
        if data is None:
            data = {}
        logger.info(f"Событие: {event_type} {data}")
        if event_type in self._subscribers:
            await asyncio.gather(
                *[cb(data) for cb in self._subscribers[event_type]],
                return_exceptions=True
            )

    def set_state(self, key: str, value: Any, publish: bool = True):
        old = self._context.get(key)
        self._context[key] = value
        if publish and old != value:
            asyncio.create_task(self.publish(f"state:{key}", {"old": old, "new": value}))
            asyncio.create_task(self.publish("state_changed", {"key": key, "old": old, "new": value}))

    def get_state(self, key: str):
        return self._context.get(key)

    def get_all_state(self):
        return self._context.copy()


_bus: Optional[EventBus] = None


def get_bus() -> EventBus:
    global _bus
    if _bus is None:
        _bus = EventBus()
    return _bus
