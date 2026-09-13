"""Canonical modeled-payload serialization for the frozen R04 amendment.

These byte counts model the monitored-wiki interface.  They are not historical
HTTP wire sizes or physical storage/RAM measurements.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence


MICROSECONDS_PER_HOUR = 3_600_000_000


def require_utc(value: datetime, field: str = "timestamp") -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field} must be a timezone-aware UTC datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must be a timezone-aware UTC datetime")
    return value.astimezone(timezone.utc)


def format_timestamp(value: datetime) -> str:
    value = require_utc(value)
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _validate_json(value: Any) -> None:
    if isinstance(value, str):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            raise ValueError("canonical JSON rejects lone Unicode surrogates")
        return
    if value is None or isinstance(value, bool):
        return
    if type(value) is int:
        if value < 0:
            raise ValueError("canonical modeled metadata integers must be nonnegative")
        return
    if isinstance(value, Enum):
        _validate_json(value.value)
        return
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise TypeError("canonical JSON object keys must be strings")
        for key, item in value.items():
            _validate_json(key)
            _validate_json(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_json(item)
        return
    raise TypeError(f"unsupported canonical JSON value: {type(value).__name__}")


def canonical_jsonl(value: Any) -> bytes:
    """Return C(x): compact sorted UTF-8 JSON followed by exactly one LF."""

    _validate_json(value)
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def canonical_array(values: Sequence[Any]) -> bytes:
    """Serialize one canonical JSON response array with one trailing LF."""

    return canonical_jsonl(list(values))


def concatenated_jsonl(values: Iterable[Any]) -> bytes:
    return b"".join(canonical_jsonl(value) for value in values)


def elapsed_microseconds(start: datetime, end: datetime) -> int:
    start = require_utc(start, "start")
    end = require_utc(end, "end")
    delta = end - start
    return delta.days * 86_400_000_000 + delta.seconds * 1_000_000 + delta.microseconds


@dataclass(frozen=True, slots=True)
class CombinedAccounting:
    final_s: int
    final_m: int
    peak_s: int
    peak_m: int
    synchronized_peak_s_plus_m: int
    s_byte_microseconds: int
    m_byte_microseconds: int
    combined_byte_microseconds: int


def synchronized_accounting(points: Sequence[tuple[datetime, int, int]],
                            checkpoint: datetime) -> CombinedAccounting:
    """Integrate exact S/M ledgers without summing independently timed peaks."""
    checkpoint = require_utc(checkpoint, "checkpoint")
    ordered = sorted(points, key=lambda x: x[0])
    s = m = peak_s = peak_m = peak_combined = s_area = m_area = 0
    last = ordered[0][0] if ordered else checkpoint
    for when, next_s, next_m in ordered:
        when = require_utc(when)
        if when < last or when > checkpoint: raise ValueError("invalid accounting point order")
        delta = elapsed_microseconds(last, when)
        s_area += s * delta; m_area += m * delta
        if min(next_s, next_m) < 0: raise ValueError("accounting bytes cannot be negative")
        s, m = next_s, next_m
        peak_s=max(peak_s,s); peak_m=max(peak_m,m); peak_combined=max(peak_combined,s+m)
        last=when
    delta=elapsed_microseconds(last,checkpoint)
    s_area+=s*delta; m_area+=m*delta
    return CombinedAccounting(s,m,peak_s,peak_m,peak_combined,s_area,m_area,s_area+m_area)


__all__ = [
    "MICROSECONDS_PER_HOUR",
    "CombinedAccounting",
    "canonical_array",
    "canonical_jsonl",
    "concatenated_jsonl",
    "elapsed_microseconds",
    "format_timestamp",
    "require_utc",
    "synchronized_accounting",
]
