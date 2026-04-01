from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from queue import Queue, Empty
from typing import Callable

from agentic_runtime.utils.time_utils import utc_now_iso


@dataclass
class Event:
    """Evento tipado que fluye por el bus."""
    topic: str
    payload: object
    ts: str = field(default_factory=utc_now_iso)
    source: str = "runtime"


# Tipo para callbacks de suscriptores
Subscriber = Callable[[Event], None]


class EventBus:
    """Bus de eventos en memoria con soporte de suscriptores por tópico.

    Uso:
        bus = EventBus()
        bus.subscribe("llm.response", lambda e: print(e.payload))
        bus.publish(Event(topic="llm.response", payload="hola"))
        bus.dispatch_all()   # ejecuta todos los suscriptores pendientes
    """

    def __init__(self) -> None:
        self._queue: Queue[Event] = Queue()
        self._subscribers: dict[str, list[Subscriber]] = defaultdict(list)
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def publish(self, event: Event) -> None:
        """Encola un evento para despacho posterior."""
        self._queue.put(event)

    def subscribe(self, topic: str, callback: Subscriber) -> None:
        """Registra un callback para un tópico específico."""
        with self._lock:
            self._subscribers[topic].append(callback)

    def dispatch_all(self) -> int:
        """Despacha todos los eventos pendientes a sus suscriptores.

        Retorna el número de eventos procesados.
        """
        count = 0
        while True:
            try:
                event = self._queue.get_nowait()
            except Empty:
                break
            self._dispatch(event)
            count += 1
        return count

    def dispatch_one(self) -> Event | None:
        """Despacha un solo evento, retorna None si la cola está vacía."""
        try:
            event = self._queue.get_nowait()
            self._dispatch(event)
            return event
        except Empty:
            return None

    def pending(self) -> int:
        """Número de eventos pendientes en la cola."""
        return self._queue.qsize()

    # ------------------------------------------------------------------
    # Interno
    # ------------------------------------------------------------------

    def _dispatch(self, event: Event) -> None:
        with self._lock:
            callbacks = list(self._subscribers.get(event.topic, []))
        for cb in callbacks:
            try:
                cb(event)
            except Exception:
                pass  # suscriptores no deben romper el flujo principal
