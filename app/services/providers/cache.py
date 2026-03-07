from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class _CacheEntry(Generic[T]):
    value: T
    expires_at: datetime


class TTLCache(Generic[T]):
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl_seconds = ttl_seconds
        self._data: dict[str, _CacheEntry[T]] = {}

    def get(self, key: str) -> T | None:
        entry = self._data.get(key)
        if not entry:
            return None
        if entry.expires_at <= datetime.now(tz=UTC):
            self._data.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: T) -> None:
        self._data[key] = _CacheEntry(
            value=value,
            expires_at=datetime.now(tz=UTC) + timedelta(seconds=self._ttl_seconds),
        )
