"""Simple in-memory event bus."""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Any, Callable, DefaultDict, Deque

EventHandler = Callable[[dict[str, Any]], None]

logger = logging.getLogger("ugc.events")


class EventBus:
    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, list[EventHandler]] = defaultdict(list)
        self._queue: Deque[tuple[str, dict[str, Any]]] = deque()

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        """Store an event in the queue and process it immediately."""
        self._queue.append((event_type, payload))
        self.dispatch()

    def dispatch(self) -> None:
        """Process all queued events sequentially."""
        while self._queue:
            event_type, payload = self._queue.popleft()
            for handler in list(self._subscribers.get(event_type, [])):
                try:
                    handler(payload)
                except Exception:  # pragma: no cover - defensive logging
                    logger.exception("Event handler failed for %s", event_type)


event_bus = EventBus()
