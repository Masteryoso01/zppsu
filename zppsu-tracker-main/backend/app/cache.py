"""In-memory cache with write-behind persistence in front of a slow backend (Google Sheets via Apps Script).

Every Apps Script call costs 1-3 s, so hitting it per request makes the app crawl. Instead:

* Each table is loaded once (all tables are warmed in parallel at startup) and then served from memory.
* Writes update memory immediately (the UI sees them at once) and are queued; one background worker
  persists them to the sheet in order, merging runs of inserts into a single call.
* A background refresher re-reads tables every `refresh_seconds` so manual edits made in the spreadsheet
  show up. It never runs while writes are pending, and never overwrites a table that changed meanwhile.

This assumes a single API process owns the data (true for this deployment). Trade-off: a write that has not
reached the sheet yet is lost if the process is killed hard. A normal shutdown flushes the queue first.
"""
import copy
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .schema import TABLES
from .store import Row, StoreError, _clean


class CachedStore:
    def __init__(self, backend, refresh_seconds: float = 60, retry_delay: float = 1.5, warm: bool = True) -> None:
        self._backend = backend
        self._retry_delay = retry_delay
        self._data: dict[str, list[Row]] = {}
        self._versions: dict[str, int] = {t: 0 for t in TABLES}
        self._lock = threading.RLock()
        self._load_locks = {t: threading.Lock() for t in TABLES}

        self._ops: deque[dict] = deque()
        self._cond = threading.Condition()
        self._inflight = False
        self._stop = threading.Event()
        self.failed: list[dict] = []

        self._worker = threading.Thread(target=self._work, name="store-writer", daemon=True)
        self._worker.start()
        if refresh_seconds > 0:
            self._refresh_seconds = refresh_seconds
            threading.Thread(target=self._refresh_loop, name="store-refresher", daemon=True).start()
        if warm:
            threading.Thread(target=self.prefetch, args=(list(TABLES),), name="store-warmup", daemon=True).start()

    # ---- loading ---------------------------------------------------------------------------

    def _table(self, table: str) -> list[Row]:
        rows = self._data.get(table)
        if rows is not None:
            return rows
        with self._load_locks[table]:  # one loader per table; concurrent callers wait for it
            rows = self._data.get(table)
            if rows is None:
                fetched = self._backend.fetch_all(table)
                with self._lock:
                    self._data[table] = fetched
                rows = fetched
        return rows

    def prefetch(self, tables: list[str]) -> None:
        todo = [t for t in tables if t not in self._data]
        if not todo:
            return
        with ThreadPoolExecutor(max_workers=len(todo)) as pool:
            list(pool.map(self._table, todo))

    # ---- reads (served from memory) --------------------------------------------------------

    def list(self, table: str, where: Row | None = None) -> list[Row]:
        rows = self._table(table)
        with self._lock:
            out = [r for r in rows if all(r.get(k) == v for k, v in (where or {}).items())]
            return copy.deepcopy(out)

    def get(self, table: str, id: str) -> Row | None:
        rows = self.list(table, {"id": id})
        return rows[0] if rows else None

    # ---- writes (memory now, sheet in the background) --------------------------------------

    def insert(self, table: str, row: Row) -> Row:
        return self.insert_many(table, [row])[0]

    def insert_many(self, table: str, rows: list[Row]) -> list[Row]:
        if not rows:
            return []
        cleaned = [_clean(table, r) for r in rows]
        self._table(table)
        with self._lock:
            self._data[table].extend(copy.deepcopy(cleaned))
            self._versions[table] += 1
        self._enqueue({"kind": "insert_many", "table": table, "rows": copy.deepcopy(cleaned)})
        return copy.deepcopy(cleaned)

    def update(self, table: str, id: str, patch: Row) -> Row | None:
        self._table(table)
        clean_patch = {k: v for k, v in patch.items() if k in TABLES[table] and k != "id"}
        with self._lock:
            for r in self._data[table]:
                if r["id"] == id:
                    r.update(clean_patch)
                    self._versions[table] += 1
                    updated = copy.deepcopy(r)
                    break
            else:
                return None
        self._enqueue({"kind": "update", "table": table, "id": id, "patch": clean_patch})
        return updated

    def delete(self, table: str, id: str) -> bool:
        self._table(table)
        with self._lock:
            before = len(self._data[table])
            self._data[table] = [r for r in self._data[table] if r["id"] != id]
            removed = len(self._data[table]) < before
            if removed:
                self._versions[table] += 1
        if removed:
            self._enqueue({"kind": "delete", "table": table, "id": id})
        return removed

    # ---- background persistence ------------------------------------------------------------

    def _enqueue(self, op: dict) -> None:
        with self._cond:
            self._ops.append(op)
            self._cond.notify_all()

    def _idle(self) -> bool:
        with self._cond:
            return not self._ops and not self._inflight

    def flush(self, timeout: float = 30) -> bool:
        """Block until every queued write has been sent to the backend (or `timeout` passes)."""
        deadline = time.monotonic() + timeout
        with self._cond:
            while self._ops or self._inflight:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                self._cond.wait(min(remaining, 0.5))
        return True

    def _work(self) -> None:
        while True:
            with self._cond:
                while not self._ops and not self._stop.is_set():
                    self._cond.wait(0.5)
                if not self._ops:
                    return  # stopping and nothing left to write
                op = self._ops.popleft()
                if op["kind"] == "insert_many":  # merge a run of inserts into one (slow) backend call
                    while self._ops and self._ops[0]["kind"] == "insert_many" and self._ops[0]["table"] == op["table"]:
                        op["rows"] = op["rows"] + self._ops.popleft()["rows"]
                self._inflight = True
            try:
                self._persist(op)
            finally:
                with self._cond:
                    self._inflight = False
                    self._cond.notify_all()

    def _persist(self, op: dict) -> None:
        for attempt in range(1, 4):
            try:
                if op["kind"] == "insert_many":
                    self._backend.insert_many(op["table"], op["rows"])
                elif op["kind"] == "update":
                    self._backend.update(op["table"], op["id"], op["patch"])
                else:
                    self._backend.delete(op["table"], op["id"])
                return
            except StoreError as e:
                if attempt == 3:
                    print(f"[store] giving up on {op['kind']} {op['table']}: {e}")
                    self.failed.append({"kind": op["kind"], "table": op["table"], "error": str(e)})
                    return
                time.sleep(self._retry_delay * attempt)

    # ---- periodic refresh from the sheet ---------------------------------------------------

    def _refresh_loop(self) -> None:
        while not self._stop.wait(self._refresh_seconds):
            self._refresh_once()

    def _refresh_once(self) -> None:
        """Re-read loaded tables so edits made directly in the spreadsheet show up.

        Skipped while writes are pending, and a table is only replaced if nothing changed it during the fetch.
        """
        for table in list(self._data):
            if not self._idle():
                return
            with self._lock:
                version = self._versions[table]
            try:
                fresh = self._backend.fetch_all(table)
            except StoreError:
                continue
            with self._lock:
                if self._versions[table] == version and self._idle():
                    self._data[table] = fresh

    # ---- housekeeping ----------------------------------------------------------------------

    def ping(self) -> bool:
        return self._backend.ping()

    def stats(self) -> dict[str, Any]:
        with self._cond:
            pending = len(self._ops) + (1 if self._inflight else 0)
        return {"pendingWrites": pending, "failedWrites": len(self.failed), "tablesCached": len(self._data)}

    def close(self) -> None:
        self.flush()
        self._stop.set()
        with self._cond:
            self._cond.notify_all()
