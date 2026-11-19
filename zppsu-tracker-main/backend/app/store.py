"""Storage backends. Both expose the same small API:

    list(table, where=None) / get(table, id) / insert(table, row) / insert_many(table, rows)
    update(table, id, patch) / delete(table, id)

`SheetsStore` talks to the Google Apps Script web app; `MemoryStore` is for local dev and tests.
"""
import copy
import ssl
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from typing import Any

import httpx

from .config import Settings
from .schema import TABLES

Row = dict[str, Any]


class StoreError(RuntimeError):
    pass


def _tls_context() -> ssl.SSLContext | bool:
    """Trust the OS certificate store (Windows/macOS) instead of Python's bundled CA list.

    Fixes `CERTIFICATE_VERIFY_FAILED` behind antivirus/proxy TLS inspection, and a stale `SSL_CERT_FILE`
    env var (e.g. left behind by XAMPP) pointing at a file that no longer exists.
    """
    try:
        import truststore

        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except ImportError:
        return True


def _clean(table: str, row: Row) -> Row:
    """Keep only known columns, fill the rest with None."""
    return {c: row.get(c) for c in TABLES[table]}


class MemoryStore:
    def __init__(self) -> None:
        self._data: dict[str, list[Row]] = {t: [] for t in TABLES}
        self._lock = threading.Lock()

    def prefetch(self, tables: list[str]) -> None:
        """No-op: in-memory reads are instant."""

    def list(self, table: str, where: Row | None = None) -> list[Row]:
        with self._lock:
            rows = [r for r in self._data[table] if all(r.get(k) == v for k, v in (where or {}).items())]
            return copy.deepcopy(rows)

    def get(self, table: str, id: str) -> Row | None:
        rows = self.list(table, {"id": id})
        return rows[0] if rows else None

    def insert(self, table: str, row: Row) -> Row:
        return self.insert_many(table, [row])[0]

    def insert_many(self, table: str, rows: list[Row]) -> list[Row]:
        with self._lock:
            cleaned = [_clean(table, r) for r in rows]
            self._data[table].extend(cleaned)
            return copy.deepcopy(cleaned)

    def update(self, table: str, id: str, patch: Row) -> Row | None:
        with self._lock:
            for r in self._data[table]:
                if r["id"] == id:
                    r.update({k: v for k, v in patch.items() if k in TABLES[table] and k != "id"})
                    return copy.deepcopy(r)
        return None

    def delete(self, table: str, id: str) -> bool:
        with self._lock:
            before = len(self._data[table])
            self._data[table] = [r for r in self._data[table] if r["id"] != id]
            return len(self._data[table]) < before


class SheetsStore:
    """Google Sheets through the Apps Script web app in apps-script/Code.gs."""

    CACHE_TTL = 5.0  # seconds; Apps Script calls are slow (~0.5-2s), so reads are briefly cached

    def __init__(self, url: str, secret: str) -> None:
        if not url or not secret:
            raise StoreError("APPS_SCRIPT_URL and APPS_SCRIPT_SECRET must be set when STORE=sheets")
        self._url = url
        self._secret = secret
        # Apps Script answers POST with a 302 to a googleusercontent URL; follow it.
        self._http = httpx.Client(timeout=60, follow_redirects=True, verify=_tls_context())
        self._cache: dict[str, tuple[float, list[Row]]] = {}
        self._lock = threading.Lock()

    # Reads are safe to repeat; writes are never retried (a retry could insert a row twice).
    READ_ACTIONS = {"ping", "list", "get"}

    def _call(self, action: str, **payload: Any) -> Any:
        attempts = 3 if action in self.READ_ACTIONS else 1
        for attempt in range(1, attempts + 1):
            try:
                res = self._http.post(self._url, json={"secret": self._secret, "action": action, **payload})
                res.raise_for_status()
                body = res.json()
                break
            except (httpx.HTTPError, ValueError) as e:
                if attempt == attempts:
                    raise StoreError(f"Apps Script request failed: {e}") from e
                time.sleep(1.5 * attempt)
        if not body.get("ok"):
            raise StoreError(f"Apps Script error: {body.get('error')}")
        return body.get("data")

    def _invalidate(self, table: str) -> None:
        with self._lock:
            self._cache.pop(table, None)

    def _all(self, table: str) -> list[Row]:
        now = time.monotonic()
        with self._lock:
            hit = self._cache.get(table)
            if hit and now - hit[0] < self.CACHE_TTL:
                return hit[1]
        rows = self._call("list", table=table)
        with self._lock:
            self._cache[table] = (now, rows)
        return rows

    def fetch_all(self, table: str) -> list[Row]:
        """Uncached read of a whole table (used by CachedStore, which does its own caching)."""
        return self._call("list", table=table)

    def prefetch(self, tables: list[str]) -> None:
        """Warm the read cache for several tables at once (each Apps Script call is slow, so run them in parallel)."""
        with ThreadPoolExecutor(max_workers=len(tables)) as pool:
            list(pool.map(self._all, tables))

    def list(self, table: str, where: Row | None = None) -> list[Row]:
        rows = self._all(table)
        if where:
            rows = [r for r in rows if all(r.get(k) == v for k, v in where.items())]
        return copy.deepcopy(rows)

    def get(self, table: str, id: str) -> Row | None:
        rows = self.list(table, {"id": id})
        return rows[0] if rows else None

    def insert(self, table: str, row: Row) -> Row:
        out = self._call("insert", table=table, row=_clean(table, row))
        self._invalidate(table)
        return out

    def insert_many(self, table: str, rows: list[Row]) -> list[Row]:
        if not rows:
            return []
        out = self._call("insert_many", table=table, rows=[_clean(table, r) for r in rows])
        self._invalidate(table)
        return out

    def update(self, table: str, id: str, patch: Row) -> Row | None:
        out = self._call("update", table=table, id=id, patch={k: v for k, v in patch.items() if k in TABLES[table]})
        self._invalidate(table)
        return out

    def delete(self, table: str, id: str) -> bool:
        out = self._call("delete", table=table, id=id)
        self._invalidate(table)
        return bool(out)

    def ping(self) -> bool:
        return self._call("ping") == "pong"


def build_store(settings: Settings):
    if settings.store == "sheets":
        from .cache import CachedStore  # local import: cache.py imports helpers from this module

        sheets = SheetsStore(settings.apps_script_url, settings.apps_script_secret)
        return CachedStore(sheets, refresh_seconds=settings.sheets_refresh_seconds)
    return MemoryStore()
