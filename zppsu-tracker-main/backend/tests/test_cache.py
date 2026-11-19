import copy
import threading
import time

import pytest

from app.cache import CachedStore
from app.schema import TABLES
from app.store import StoreError


class FakeBackend:
    """Stands in for SheetsStore: same methods, plus call recording and an optional per-call delay."""

    def __init__(self, delay: float = 0.0):
        self.tables = {t: [] for t in TABLES}
        self.calls: list[tuple] = []
        self.delay = delay
        self.fail = False
        self._lock = threading.Lock()

    def _enter(self, *call):
        with self._lock:
            self.calls.append(call)
        time.sleep(self.delay)
        if self.fail:
            raise StoreError("boom")

    def fetch_all(self, table):
        self._enter("fetch", table)
        return copy.deepcopy(self.tables[table])

    def insert_many(self, table, rows):
        self._enter("insert_many", table, len(rows))
        self.tables[table].extend(copy.deepcopy(rows))
        return rows

    def update(self, table, id, patch):
        self._enter("update", table, id)
        for r in self.tables[table]:
            if r["id"] == id:
                r.update(patch)

    def delete(self, table, id):
        self._enter("delete", table, id)
        self.tables[table] = [r for r in self.tables[table] if r["id"] != id]

    def ping(self):
        return True


def make(delay=0.0, **kw):
    backend = FakeBackend(delay)
    return backend, CachedStore(backend, refresh_seconds=0, retry_delay=0.01, warm=False, **kw)


def org(i):
    return {"id": f"org-{i}", "name": f"Org {i}", "address": "x", "status": "Active", "createdAt": "2026-01-01"}


def test_reads_hit_the_backend_once_per_table():
    backend, store = make()
    backend.tables["organizations"] = [org(1)]
    for _ in range(5):
        assert store.list("organizations")[0]["id"] == "org-1"
        assert store.get("organizations", "org-1")["name"] == "Org 1"
    assert [c for c in backend.calls if c[0] == "fetch"] == [("fetch", "organizations")]


def test_writes_are_visible_instantly_and_persisted_in_order():
    backend, store = make(delay=0.15)
    start = time.monotonic()
    store.insert("organizations", org(1))
    store.update("organizations", "org-1", {"name": "Renamed"})
    assert time.monotonic() - start < 0.2 + 0.15  # only the initial table load may wait; the writes themselves don't
    assert store.get("organizations", "org-1")["name"] == "Renamed"  # visible before the sheet has it
    assert backend.tables["organizations"] == []
    assert store.flush(5)
    assert backend.tables["organizations"][0]["name"] == "Renamed"  # insert ran before the update
    assert store.stats()["pendingWrites"] == 0


def test_consecutive_inserts_are_merged_into_few_backend_calls():
    backend, store = make(delay=0.15)
    for i in range(6):
        store.insert("organizations", org(i))
    assert store.flush(10)
    assert len(backend.tables["organizations"]) == 6
    inserts = [c for c in backend.calls if c[0] == "insert_many"]
    assert len(inserts) < 6 and sum(c[2] for c in inserts) == 6


def test_delete_and_missing_rows():
    backend, store = make()
    backend.tables["organizations"] = [org(1)]
    assert store.update("organizations", "nope", {"name": "x"}) is None
    assert store.delete("organizations", "nope") is False
    assert store.delete("organizations", "org-1") is True
    assert store.list("organizations") == []
    assert store.flush(5) and backend.tables["organizations"] == []
    assert not [c for c in backend.calls if c[0] == "delete" and c[2] == "nope"]  # no-ops are not sent


def test_returned_rows_are_copies():
    _, store = make()
    store.insert("organizations", org(1))
    store.list("organizations")[0]["name"] = "tampered"
    assert store.get("organizations", "org-1")["name"] == "Org 1"


def test_refresh_picks_up_manual_sheet_edits_but_never_clobbers_pending_writes():
    backend, store = make(delay=0.2)
    backend.tables["organizations"] = [org(1)]
    store.list("organizations")  # load
    backend.tables["organizations"].append(org(2))  # someone edits the spreadsheet by hand

    store.insert("organizations", org(3))  # pending write
    store._refresh_once()  # must be skipped: a write is waiting
    assert {o["id"] for o in store.list("organizations")} == {"org-1", "org-3"}

    assert store.flush(5)
    store._refresh_once()  # idle now: the manual edit shows up, the persisted write is still there
    assert {o["id"] for o in store.list("organizations")} == {"org-1", "org-2", "org-3"}


def test_backend_failure_is_retried_then_recorded():
    backend, store = make()
    store.list("organizations")
    backend.fail = True
    store.insert("organizations", org(1))
    assert store.flush(5)
    assert store.stats()["failedWrites"] == 1 and store.failed[0]["table"] == "organizations"
    assert len([c for c in backend.calls if c[0] == "insert_many"]) == 3  # three attempts
    assert store.get("organizations", "org-1")  # the app keeps working from memory


def test_prefetch_loads_tables_in_parallel_and_close_flushes():
    backend, store = make(delay=0.2)
    t0 = time.monotonic()
    store.prefetch(["organizations", "users", "interns", "attendance"])
    assert time.monotonic() - t0 < 0.5  # 4 loads x 0.2 s would be 0.8 s if sequential
    store.insert("organizations", org(1))
    store.close()
    assert backend.tables["organizations"][0]["id"] == "org-1"
