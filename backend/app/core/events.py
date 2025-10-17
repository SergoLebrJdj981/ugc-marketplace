"""Simple in-memory event bus."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, DefaultDict

EventHandler = Callable[[dict[str, Any]], None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        for handler in self._subscribers.get(event_type, []):
            handler(payload)

    dispatch = publish


event_bus = EventBus()
