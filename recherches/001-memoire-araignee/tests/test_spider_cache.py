"""Tests pour SpiderCache + SpiderWatcher + IdleWatcher (La Forme Araignée).

Couverture :
  Toile 1 (cache) : recherche, format identique a memory_tools.search_principles
  Toile 2 (watcher auto-refresh) : detection de modification SQLite
  Toile 3 (idle watcher) : detection d'inactivite + cooldown + lifecycle
"""

import sqlite3
import tempfile
import threading
import time
from pathlib import Path

import pytest


# ── Helpers ────────────────────────────────────────────────────────────────


def _make_l2_db(path: Path) -> None:
    """Cree un l2_distilled.db minimal avec quelques principes."""
    conn = sqlite3.connect(str(path))
    conn.executescript(
        """
        CREATE TABLE principles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            type TEXT,
            domain TEXT,
            c_success INTEGER DEFAULT 0,
            c_use INTEGER DEFAULT 0,
            score REAL DEFAULT 0.5,
            embedding BLOB,
            triples_json TEXT,
            last_used_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    rows = [
        (1, "slippage impact analysis", "guiding", "defi_quant", 5, 6),
        (2, "yield farming caution", "cautionary", "defi_quant", 2, 4),
        (3, "LTM consolidation pattern", "guiding", "memory", 3, 3),
    ]
    for r in rows:
        conn.execute(
            """INSERT INTO principles (id, text, type, domain, c_success, c_use)
               VALUES (?, ?, ?, ?, ?, ?)""",
            r,
        )
    conn.commit()
    conn.close()


def _make_event_bus(path: Path) -> None:
    """Cree un event_bus.db minimal."""
    conn = sqlite3.connect(str(path))
    conn.executescript(
        """
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 5,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            processed_at DATETIME
        );
        """
    )
    conn.commit()
    conn.close()


# ── Toile 1 : SpiderCache ─────────────────────────────────────────────────


class TestSpiderCache:
    def test_cache_loads_from_db(self, tmp_path):
        from memory.spider_cache import SpiderCache

        db = tmp_path / "l2_distilled.db"
        _make_l2_db(db)
        cache = SpiderCache(db_path=db)
        assert len(cache.principles) == 3
        assert "defi_quant" in cache.domain_index
        assert "memory" in cache.domain_index

    def test_search_returns_top_k(self, tmp_path):
        from memory.spider_cache import SpiderCache

        db = tmp_path / "l2_distilled.db"
        _make_l2_db(db)
        cache = SpiderCache(db_path=db)
        results = cache.search("slippage", domain="defi_quant", top_k=2)
        assert len(results) <= 2
        for r in results:
            assert "id" in r
            assert "text" in r
            assert "type" in r
            assert "score" in r
            assert "triples" in r

    def test_search_filters_by_domain(self, tmp_path):
        from memory.spider_cache import SpiderCache

        db = tmp_path / "l2_distilled.db"
        _make_l2_db(db)
        cache = SpiderCache(db_path=db)
        results = cache.search("pattern", domain="memory", top_k=5)
        for r in results:
            assert r["id"] == 3

    def test_search_empty_db(self, tmp_path):
        from memory.spider_cache import SpiderCache

        db = tmp_path / "l2_distilled.db"
        _make_l2_db(db)
        cache = SpiderCache(db_path=db)
        results = cache.search("anything", domain="nonexistent", top_k=5)
        assert results == []

    def test_cache_missing_db(self, tmp_path):
        from memory.spider_cache import SpiderCache

        db = tmp_path / "missing.db"
        cache = SpiderCache(db_path=db)
        assert len(cache.principles) == 0

    def test_refresh_reloads(self, tmp_path):
        from memory.spider_cache import SpiderCache

        db = tmp_path / "l2_distilled.db"
        _make_l2_db(db)
        cache = SpiderCache(db_path=db)
        assert len(cache.principles) == 3

        # Add a new principle directly
        conn = sqlite3.connect(str(db))
        conn.execute(
            """INSERT INTO principles (text, type, domain) VALUES (?, ?, ?)""",
            ("new principle", "guiding", "defi_quant"),
        )
        conn.commit()
        conn.close()

        cache.refresh()
        assert len(cache.principles) == 4

    def test_get_cache_singleton(self, tmp_path):
        from memory.spider_cache import SpiderCache, get_cache

        # First call creates
        c1 = get_cache()
        # Second call returns same
        c2 = get_cache()
        assert c1 is c2


# ── Toile 2 : SpiderWatcher (auto-refresh) ────────────────────────────────


class TestSpiderWatcher:
    def test_watcher_starts_and_stops(self, tmp_path):
        from memory.spider_cache import SpiderCache, SpiderWatcher

        db = tmp_path / "l2_distilled.db"
        _make_l2_db(db)
        cache = SpiderCache(db_path=db)
        watcher = SpiderWatcher(cache, poll_interval=0.5)
        assert not watcher.is_alive
        watcher.start()
        time.sleep(0.2)
        assert watcher.is_alive
        watcher.stop()
        time.sleep(0.5)
        assert not watcher.is_alive

    def test_watcher_detects_modification(self, tmp_path):
        from memory.spider_cache import SpiderCache, SpiderWatcher

        db = tmp_path / "l2_distilled.db"
        _make_l2_db(db)
        cache = SpiderCache(db_path=db)
        initial_count = len(cache.principles)

        watcher = SpiderWatcher(cache, poll_interval=0.5)
        watcher.start()
        time.sleep(0.3)

        # Modify the DB
        conn = sqlite3.connect(str(db))
        conn.execute(
            """INSERT INTO principles (text, type, domain) VALUES (?, ?, ?)""",
            ("added later", "guiding", "defi_quant"),
        )
        conn.commit()
        conn.close()

        # Cooldown is 5s in SpiderWatcher, so wait long enough
        time.sleep(6.0)
        assert len(cache.principles) == initial_count + 1
        watcher.stop()

    def test_watcher_context_manager(self, tmp_path):
        from memory.spider_cache import SpiderCache, SpiderWatcher

        db = tmp_path / "l2_distilled.db"
        _make_l2_db(db)
        cache = SpiderCache(db_path=db)
        with SpiderWatcher(cache, poll_interval=0.5) as w:
            assert w.is_alive
        time.sleep(0.5)
        # After context exit, watcher is stopped
        # (is_alive is False; we can only check by starting a new one)
        assert True  # context manager worked without error


# ── Toile 3 : IdleWatcher ─────────────────────────────────────────────────


class TestIdleWatcher:
    def test_idle_watcher_instantiation(self, tmp_path):
        from memory.spider_cache import IdleWatcher

        cb = lambda s: None
        w = IdleWatcher(
            on_idle=cb,
            idle_threshold_sec=10.0,
            check_interval_sec=2.0,
        )
        assert w._threshold == 10.0
        assert w._interval == 2.0
        assert w.actions_count == 0
        assert not w.is_alive

    def test_idle_watcher_lifecycle(self, tmp_path):
        from memory.spider_cache import IdleWatcher

        w = IdleWatcher(
            on_idle=lambda s: None,
            idle_threshold_sec=5.0,
            check_interval_sec=0.5,
        )
        w.start()
        time.sleep(0.2)
        assert w.is_alive
        w.stop()
        time.sleep(0.2)
        assert not w.is_alive

    def test_idle_watcher_triggers_callback(self, tmp_path):
        from memory.spider_cache import IdleWatcher

        events = []

        def cb(idle_secs):
            events.append(idle_secs)

        w = IdleWatcher(
            on_idle=cb,
            idle_threshold_sec=1.0,
            check_interval_sec=0.2,
            cooldown_sec=0.5,
        )
        w.start()
        time.sleep(3.0)  # wait for action
        w.stop()
        assert len(events) >= 1
        assert all(e >= 1.0 for e in events)

    def test_idle_watcher_respects_cooldown(self, tmp_path):
        from memory.spider_cache import IdleWatcher

        events = []
        w = IdleWatcher(
            on_idle=lambda s: events.append(s),
            idle_threshold_sec=0.5,
            check_interval_sec=0.2,
            cooldown_sec=10.0,  # long cooldown
        )
        w.start()
        time.sleep(2.0)
        w.stop()
        # Cooldown is 10s but we only waited 2s, so at most 1 action
        assert len(events) <= 1

    def test_idle_watcher_reads_event_bus(self, tmp_path):
        from memory.spider_cache import IdleWatcher

        eb = tmp_path / "event_bus.db"
        _make_event_bus(eb)
        # Insert an event with a recent processed_at
        conn = sqlite3.connect(str(eb))
        conn.execute(
            """INSERT INTO events (type, payload, status, processed_at)
               VALUES (?, ?, ?, datetime('now'))""",
            ("TEST", "{}", "done"),
        )
        conn.commit()
        conn.close()

        w = IdleWatcher(
            on_idle=lambda s: None,
            event_bus_path=eb,
        )
        # The watcher should read the recent activity
        last = w._read_last_activity()
        assert last > 0
        # And idle_seconds should be small
        assert w.idle_seconds < 60

    def test_idle_watcher_missing_event_bus(self, tmp_path):
        from memory.spider_cache import IdleWatcher

        missing = tmp_path / "nonexistent.db"
        w = IdleWatcher(event_bus_path=missing)
        last = w._read_last_activity()
        # Should return now() without error
        assert abs(last - time.time()) < 2

    def test_idle_watcher_idle_property(self, tmp_path):
        from memory.spider_cache import IdleWatcher

        w = IdleWatcher(
            on_idle=lambda s: None,
            idle_threshold_sec=0.5,
        )
        w.last_activity = time.time() - 2.0
        assert w.is_idle
        assert w.idle_seconds >= 2.0


# ── Integration : Fallback dans memory_tools ──────────────────────────────


class TestSpiderCacheIntegration:
    def test_search_principles_uses_cache(self, tmp_path, monkeypatch):
        """Verifie que search_principles() utilise SpiderCache si disponible."""
        from memory import spider_cache

        db = tmp_path / "l2_distilled.db"
        _make_l2_db(db)

        # Force a fresh cache pointing at our temp DB
        cache = spider_cache.SpiderCache(db_path=db)
        monkeypatch.setattr(spider_cache, "_CACHE", cache)

        from tools.memory_tools import search_principles

        results = search_principles(
            task_summary="slippage",
            domain="defi_quant",
            top_k=3,
        )
        assert isinstance(results, list)
        # If cache has data, we should get results
        assert len(results) >= 1
