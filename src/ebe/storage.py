"""Neutral deterministic capture storage for later E09/E10 policies."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Literal

from .accounting import MICROSECONDS_PER_HOUR, canonical_jsonl, elapsed_microseconds, format_timestamp, require_utc
from .timeline import HORIZON_START


class StorageError(RuntimeError):
    """Base class for invalid or unsupported store operations."""


class AdmissionOrderError(StorageError):
    """Capture completions were supplied outside the frozen FIFO ordering."""


class HashCollisionError(StorageError):
    """Equal SHA-256 digests were observed for unequal canonical bodies."""


@dataclass(frozen=True, slots=True)
class Capture:
    page_key: str
    capture_time: datetime
    request_seq: int
    body: bytes

    def __post_init__(self) -> None:
        require_utc(self.capture_time, "capture_time")
        if not isinstance(self.page_key, str):
            raise TypeError("page_key must be an opaque string")
        if type(self.request_seq) is not int or self.request_seq < 1:
            raise ValueError("request_seq must be a positive integer")
        if not isinstance(self.body, bytes):
            raise TypeError("body must be canonical UTF-8 bytes")
        try:
            self.body.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ValueError("body must be valid canonical UTF-8") from exc

    @property
    def body_sha256(self) -> str:
        return sha256(self.body).hexdigest()

    @property
    def packet(self) -> dict[str, object]:
        return {
            "body_sha256": self.body_sha256,
            "capture_time": format_timestamp(self.capture_time),
            "page_key": self.page_key,
            "request_seq": self.request_seq,
        }

    @property
    def packet_bytes(self) -> bytes:
        return canonical_jsonl(self.packet)


@dataclass(frozen=True, slots=True)
class RetainedCapture:
    page_key: str
    capture_time: datetime
    request_seq: int
    body_sha256: str
    packet_bytes: bytes
    object_id: str


@dataclass(slots=True)
class _BodyObject:
    body: bytes
    refcount: int


@dataclass(frozen=True, slots=True)
class AdmissionResult:
    disposition: Literal["admitted", "oversize"]
    request_seq: int
    packet_bytes: int
    body_bytes: int
    standalone_bytes: int
    marginal_bytes: int | None
    evicted_request_seqs: tuple[int, ...]
    store_bytes: int


@dataclass(frozen=True, slots=True)
class StorageAuditRecord:
    request_seq: int
    page_key: str
    capture_time: datetime
    body_sha256: str
    body_bytes: int
    packet_bytes: int
    disposition: Literal["admitted", "oversize"]
    evicted_request_seqs: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class StorageSnapshot:
    retained_packet_bytes: int
    retained_body_bytes: int
    retained_packets: int
    retained_body_objects: int
    object_reference_counts: tuple[int, ...]
    retained_request_seqs: tuple[int, ...]
    current_store_bytes: int
    peak_store_bytes: int
    final_store_bytes: int
    evicted_packet_bytes: int
    evicted_body_bytes: int
    bytes_evicted: int
    admitted_packets: int
    rejected_oversize_packets: int
    store_byte_microseconds: int

    @property
    def store_byte_hours(self) -> float:
        return self.store_byte_microseconds / MICROSECONDS_PER_HOUR


class CaptureStore:
    """A capped FIFO packet/body store with an explicitly selected dedup mode."""

    def __init__(
        self,
        capacity_bytes: int | None,
        *,
        deduplicate: bool,
        start_time: datetime = HORIZON_START,
    ) -> None:
        if capacity_bytes is not None and (type(capacity_bytes) is not int or capacity_bytes < 0):
            raise ValueError("capacity_bytes must be a nonnegative integer or None")
        if not isinstance(deduplicate, bool):
            raise TypeError("deduplicate must be boolean")
        self.capacity_bytes = capacity_bytes
        self.deduplicate = deduplicate
        self._packets: deque[RetainedCapture] = deque()
        self._objects: dict[str, _BodyObject] = {}
        self._seen_request_seqs: set[int] = set()
        self._last_order: tuple[datetime, int, str] | None = None
        self._last_time = require_utc(start_time, "start_time")
        self._packet_bytes = 0
        self._body_bytes = 0
        self._peak_bytes = 0
        self._byte_microseconds = 0
        self._evicted_packet_bytes = 0
        self._evicted_body_bytes = 0
        self._admitted = 0
        self._oversize = 0
        self._audit: list[StorageAuditRecord] = []
        self._size_history: list[int] = [0]

    @property
    def current_bytes(self) -> int:
        return self._packet_bytes + self._body_bytes

    @property
    def retained_captures(self) -> tuple[RetainedCapture, ...]:
        return tuple(self._packets)

    @property
    def audit_records(self) -> tuple[StorageAuditRecord, ...]:
        return tuple(self._audit)

    @property
    def size_history(self) -> tuple[int, ...]:
        return tuple(self._size_history)

    def _advance(self, timestamp: datetime) -> None:
        timestamp = require_utc(timestamp)
        delta = elapsed_microseconds(self._last_time, timestamp)
        if delta < 0:
            raise AdmissionOrderError("storage operations must be supplied in completion-time order")
        self._byte_microseconds += self.current_bytes * delta
        self._last_time = timestamp

    def _object_id(self, capture: Capture) -> str:
        return capture.body_sha256 if self.deduplicate else f"{capture.request_seq}:{capture.body_sha256}"

    def _has_equal_shared_body(self, capture: Capture) -> bool:
        if not self.deduplicate:
            return False
        existing = self._objects.get(capture.body_sha256)
        if existing is None:
            return False
        if existing.body != capture.body:
            raise HashCollisionError("SHA-256 collision between unequal canonical bodies")
        return True

    def _evict_oldest(self) -> int:
        oldest = self._packets.popleft()
        packet_len = len(oldest.packet_bytes)
        self._packet_bytes -= packet_len
        self._evicted_packet_bytes += packet_len
        obj = self._objects[oldest.object_id]
        obj.refcount -= 1
        if obj.refcount == 0:
            body_len = len(obj.body)
            self._body_bytes -= body_len
            self._evicted_body_bytes += body_len
            del self._objects[oldest.object_id]
        self._size_history.append(self.current_bytes)
        return oldest.request_seq

    def admit(self, capture: Capture) -> AdmissionResult:
        order = (require_utc(capture.capture_time), capture.request_seq, capture.page_key)
        if self._last_order is not None and order < self._last_order:
            raise AdmissionOrderError("admissions must follow (response_time, request_seq, page_key)")
        if capture.request_seq in self._seen_request_seqs:
            raise StorageError(f"request_seq {capture.request_seq} was already presented")
        self._last_order = order
        self._seen_request_seqs.add(capture.request_seq)
        self._advance(capture.capture_time)

        packet = capture.packet_bytes
        p, b = len(packet), len(capture.body)
        standalone = p + b
        if self.capacity_bytes is not None and standalone > self.capacity_bytes:
            self._oversize += 1
            self._size_history.append(self.current_bytes)
            audit = StorageAuditRecord(
                capture.request_seq, capture.page_key, capture.capture_time,
                capture.body_sha256, b, p, "oversize", (),
            )
            self._audit.append(audit)
            return AdmissionResult("oversize", capture.request_seq, p, b, standalone, None, (), self.current_bytes)

        shared = self._has_equal_shared_body(capture)
        marginal = p + (0 if shared else b)
        evicted: list[int] = []
        while self.capacity_bytes is not None and self.current_bytes + marginal > self.capacity_bytes:
            if not self._packets:
                raise StorageError("admission cannot fit despite passing intrinsic oversize test")
            evicted.append(self._evict_oldest())
            shared = self._has_equal_shared_body(capture)
            marginal = p + (0 if shared else b)

        object_id = self._object_id(capture)
        obj = self._objects.get(object_id)
        if obj is None:
            obj = _BodyObject(capture.body, 0)
            self._objects[object_id] = obj
            self._body_bytes += b
        elif obj.body != capture.body:
            raise HashCollisionError("object identifier collision between unequal bodies")
        obj.refcount += 1
        retained = RetainedCapture(
            capture.page_key, capture.capture_time, capture.request_seq,
            capture.body_sha256, packet, object_id,
        )
        self._packets.append(retained)
        self._packet_bytes += p
        self._admitted += 1
        self._peak_bytes = max(self._peak_bytes, self.current_bytes)
        self._size_history.append(self.current_bytes)
        self._audit.append(StorageAuditRecord(
            capture.request_seq, capture.page_key, capture.capture_time,
            capture.body_sha256, b, p, "admitted", tuple(evicted),
        ))
        if self.capacity_bytes is not None and self.current_bytes > self.capacity_bytes:
            raise AssertionError("store capacity invariant violated")
        return AdmissionResult(
            "admitted", capture.request_seq, p, b, standalone, marginal,
            tuple(evicted), self.current_bytes,
        )

    def body_for_capture(self, request_seq: int) -> bytes:
        """Read a currently retained body; evicted bodies have no fallback cache."""

        for packet in self._packets:
            if packet.request_seq == request_seq:
                return self._objects[packet.object_id].body
        raise KeyError(request_seq)

    def snapshot(self, checkpoint: datetime | None = None) -> StorageSnapshot:
        accrued = self._byte_microseconds
        if checkpoint is not None:
            checkpoint = require_utc(checkpoint, "checkpoint")
            delta = elapsed_microseconds(self._last_time, checkpoint)
            if delta < 0:
                raise AdmissionOrderError("checkpoint precedes the latest storage operation")
            accrued += self.current_bytes * delta
        return StorageSnapshot(
            self._packet_bytes,
            self._body_bytes,
            len(self._packets),
            len(self._objects),
            tuple(sorted(obj.refcount for obj in self._objects.values())),
            tuple(packet.request_seq for packet in self._packets),
            self.current_bytes,
            self._peak_bytes,
            self.current_bytes,
            self._evicted_packet_bytes,
            self._evicted_body_bytes,
            self._evicted_packet_bytes + self._evicted_body_bytes,
            self._admitted,
            self._oversize,
            accrued,
        )


__all__ = [
    "AdmissionOrderError", "AdmissionResult", "Capture", "CaptureStore",
    "HashCollisionError", "RetainedCapture", "StorageAuditRecord", "StorageError",
    "StorageSnapshot",
]
