"""SpiderCache — Hot RAM cache pour les principes L2.

Au lieu de requêter SQLite + decoder les BLOBs + calculer BM25/cosine
à chaque appel, SpiderCache charge TOUT en RAM au démarrage et sert
les recherches en < 1ms.

Utilisation:
    from memory.spider_cache import SpiderCache
    cache = SpiderCache()
    results = cache.search("analyse du slippage", domain="defi_quant", top_k=5)
    cache.refresh()  # après une distillation
"""

import json
import math
import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional

_L2_DB_PATH = Path(__file__).parent / "l2_distilled.db"


class _Principle:
    """Un principe en RAM — embedding déjà décodé en numpy array."""

    __slots__ = (
        "id",
        "text",
        "type",
        "domain",
        "score",
        "embedding",
        "triples",
        "last_used_at",
        "days_idle",
    )

    def __init__(self, row: dict):
        self.id = row["id"]
        self.text = row["text"]
        self.type = row["type"]
        self.domain = row["domain"]
        self.score = row["score"]
        self.triples = row.get("triples", [])
        self.last_used_at = row.get("last_used_at")
        self.days_idle = row.get("days_idle", 0.0)

    def __repr__(self):
        return f"<Principle id={self.id} domain={self.domain} score={self.score:.3f}>"


class SpiderCache:
    """Cache RAM des principes L2.

    Attributs d'état (lisibles pour debug) :
        principles : list[_Principle]       — tous les principes en RAM
        domain_index : dict[str, list[int]] — domaine → indices dans principles
        loaded_at : float                   — timestamp du dernier load/refresh
        principle_count : int               — nombre total de principes
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or _L2_DB_PATH
        self.principles: list[_Principle] = []
        self.domain_index: dict[str, list[int]] = {}
        self.loaded_at: float = 0.0
        self._load()

    # ── Chargement ────────────────────────────────────────────────────────

    def _load(self):
        """Charge tous les principes depuis SQLite dans la RAM."""
        if not self._db_path.exists():
            self.principles = []
            self.domain_index = {}
            self.loaded_at = time.time()
            return

        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """SELECT id, text, type, domain, score, embedding, triples_json,
                          last_used_at,
                          CAST(julianday('now') - julianday(COALESCE(last_used_at, datetime('now'))) AS REAL)
                          AS days_idle
                   FROM principles
                   ORDER BY score DESC"""
            ).fetchall()
        except sqlite3.OperationalError:
            rows = conn.execute(
                """SELECT id, text, type, domain, score, NULL AS embedding,
                          NULL AS triples_json, NULL AS last_used_at,
                          0.0 AS days_idle
                   FROM principles
                   ORDER BY score DESC"""
            ).fetchall()
        finally:
            conn.close()

        self.principles = []
        self.domain_index = {}
        for row in rows:
            p = _Principle(
                {
                    "id": row["id"],
                    "text": row["text"],
                    "type": row["type"],
                    "domain": row["domain"],
                    "score": row["score"],
                    "last_used_at": row["last_used_at"],
                    "days_idle": float(row["days_idle"] or 0.0),
                }
            )
            # Décoder le BLOB embedding une fois pour toutes
            blob = row["embedding"]
            if blob:
                try:
                    import numpy as np

                    p.embedding = np.frombuffer(blob, dtype=np.float32)
                except Exception:
                    p.embedding = None
            else:
                p.embedding = None
            # Parser les triples
            triples_json = row["triples_json"]
            if triples_json:
                try:
                    p.triples = json.loads(triples_json)
                except Exception:
                    p.triples = []
            idx = len(self.principles)
            self.principles.append(p)
            dom = p.domain or "general"
            self.domain_index.setdefault(dom, []).append(idx)

        self.loaded_at = time.time()

    # ── Recherche ─────────────────────────────────────────────────────────

    def search(
        self,
        task_summary: str,
        domain: str,
        top_k: int = 5,
    ) -> list[dict]:
        """Même interface que memory_tools.search_principles().

        Calcule BM25 + cosine + score + decay exactement comme l'original,
        mais depuis la RAM — pas de SQLite, pas de np.frombuffer à chaque appel.
        """
        if not self.principles:
            return []

        query_words = set(task_summary.lower().split())
        if not query_words:
            return []

        # Embedding de la requête (appel à sentence-transformers, incompressible)
        query_emb = self._embed_query(task_summary)

        # Indices des principes du domaine demandé
        indices = self.domain_index.get(domain, [])
        if not indices:
            return []

        scored = []
        for idx in indices:
            p = self.principles[idx]

            # BM25 : proportion de mots de la requête présents dans le texte
            principle_words = p.text.lower().split()
            bm25 = len(query_words & set(principle_words)) / max(len(query_words), 1)

            # Score cosine : si on a l'embedding du principe ET celui de la requête
            cosine = 0.0
            if query_emb is not None and p.embedding is not None:
                try:
                    cosine = float(np.dot(query_emb, p.embedding))
                except Exception:
                    cosine = 0.0

            # Décroissance temporelle : plus un principe est vieux, moins il compte
            decay = math.exp(-0.01 * p.days_idle)

            # Score combiné (formule identique à l'original)
            combined = bm25 + cosine * 0.5 + p.score * 0.3 * decay

            scored.append((combined, p))

        scored.sort(key=lambda x: x[0], reverse=True)

        result = []
        for _, p in scored[:top_k]:
            result.append(
                {
                    "id": p.id,
                    "text": p.text,
                    "type": p.type,
                    "score": p.score,
                    "triples": p.triples,
                }
            )

        return result

    # ── Utilitaires ───────────────────────────────────────────────────────

    _embedder = None

    def _embed_query(self, text: str):
        """Lazy-load sentence-transformers, retourne le vecteur normalisé."""
        import numpy as np

        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer

                SpiderCache._embedder = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                return None
        try:
            vec = self._embedder.encode(text, normalize_embeddings=True)
            return vec.astype(np.float32)
        except Exception:
            return None

    def refresh(self):
        """Recharge tous les principes depuis SQLite (après une distillation)."""
        self._load()

    def invalidate(self, domain: str):
        """Marque un domaine comme périmé — le prochain search() le rechargera.

        Pour l'instant, refresh() complet. On optimisera plus tard.
        """
        self._load()

    def __repr__(self):
        return (
            f"<SpiderCache principles={len(self.principles)} "
            f"domains={len(self.domain_index)} "
            f"loaded={self.loaded_at:.1f}s>"
        )


# ── Watcher auto-refresh (Toile 2) ──────────────────────────────────────


class SpiderWatcher:
    """Surveille les modifications de l2_distilled.db et refresh le cache.

    Utilise watchdog (inotify/LibeV/directory watchdog selon l OS) pour
    détecter les écritures. Fallback polling si watchdog indisponible.

    Utilisation:
        from memory.spider_cache import get_cache, SpiderWatcher
        cache = get_cache()
        watcher = SpiderWatcher(cache)
        watcher.start()   # thread daemon background
        ...
        watcher.stop()
    """

    _COOLDOWN_SEC = 5.0  # pas plus d un refresh toutes les 5s

    def __init__(
        self,
        cache: SpiderCache,
        poll_interval: float = 3.0,
    ):
        self._cache = cache
        self._db_path = cache._db_path
        self._poll_interval = poll_interval
        self._last_refresh: float = 0.0
        self._last_mtime: float = cache.loaded_at
        self._observer = None
        self._poll_thread = None
        self._stop_event = None

    # ── API publique ────────────────────────────────────────────────────

    def start(self):
        """Démarre la surveillance en arrière-plan."""
        if self._observer is not None:
            return
        # Mettre à jour le mtime de référence (évite un refresh immédiat)
        self._last_mtime = (
            self._db_path.stat().st_mtime if self._db_path.exists() else 0.0
        )

        # Essayer watchdog (events filesystem natifs)
        if self._start_watchdog():
            return
        # Fallback : polling thread
        self._start_polling()

    def stop(self):
        """Arrête la surveillance."""
        if self._observer:
            try:
                self._observer.stop()
                self._observer.join(timeout=3)
            except Exception:
                pass
            self._observer = None
        if self._poll_thread:
            self._stop_event = True
            self._poll_thread = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    # ── Watchdog (events filesystem natifs) ─────────────────────────────

    def _start_watchdog(self) -> bool:
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class _Handler(FileSystemEventHandler):
                def __init__(self, watcher):
                    self.watcher = watcher

                def on_modified(self, event):
                    if event.is_directory:
                        return
                    if (
                        Path(event.src_path).resolve()
                        == self.watcher._db_path.resolve()
                    ):
                        self.watcher._on_file_changed()

            self._observer = Observer()
            self._observer.schedule(
                _Handler(self),
                str(self._db_path.parent),
                recursive=False,
            )
            self._observer.daemon = True
            self._observer.start()
            return True
        except Exception:
            self._observer = None
            return False

    # ── Fallback polling ────────────────────────────────────────────────

    def _start_polling(self):
        import threading

        self._stop_event = False

        def _poll():
            while not self._stop_event:
                time.sleep(self._poll_interval)
                try:
                    if self._db_path.exists():
                        mtime = self._db_path.stat().st_mtime
                        if mtime > self._last_mtime:
                            self._on_file_changed()
                            self._last_mtime = mtime
                except Exception:
                    pass

        self._poll_thread = threading.Thread(target=_poll, daemon=True)
        self._poll_thread.start()

    # ── Logique de refresh ──────────────────────────────────────────────

    def _on_file_changed(self):
        """Appelé quand le fichier DB est modifié.

        Applique un cooldown pour éviter les thrash (souvent plusieurs
        events pour une même écriture SQLite).
        """
        now = time.time()
        if now - self._last_refresh < self._COOLDOWN_SEC:
            return
        self._last_refresh = now
        try:
            self._cache.refresh()
        except Exception as exc:
            pass  # silent — le prochain appel search() utilisera l ancien cache

    @property
    def is_alive(self) -> bool:
        """True si le watcher est en cours d exécution."""
        if self._observer:
            return self._observer.is_alive()
        if self._poll_thread:
            return self._poll_thread.is_alive()
        return False


# Singleton au niveau module — tous les appels partagent la même RAM
_CACHE: Optional[SpiderCache] = None
_WATCHER: Optional[SpiderWatcher] = None
_IDLE: Optional["IdleWatcher"] = None


def get_cache() -> SpiderCache:
    global _CACHE
    if _CACHE is None:
        _CACHE = SpiderCache()
    return _CACHE


def start_watcher(cache: Optional[SpiderCache] = None) -> SpiderWatcher:
    """Démarre le watcher auto-refresh (singleton).

    Appel une fois au démarrage du robot (dans run_windows.ps1 ou
    orchestrator.py). Le watcher tourne en arrière-plan et refresh
    le cache automatiquement quand l2_distilled.db est modifié.
    """
    global _WATCHER
    if _WATCHER is not None:
        return _WATCHER
    if cache is None:
        cache = get_cache()
    _WATCHER = SpiderWatcher(cache)
    _WATCHER.start()
    return _WATCHER


# ── IdleWatcher (Toile 3) ──────────────────────────────────────────────


class IdleWatcher:
    """Surveille l'inactivité du robot et déclenche des actions background.

    Détecte les fenêtres d'inactivité (aucun event traité depuis N secondes)
    et exécute une callback configurable. Permet au cache de se
    pré-chauffer, de consolider, de nettoyer, etc., pendant les creux.

    Utilisation:
        watcher = IdleWatcher(
            on_idle=lambda secs: do_something_useful(),
            idle_threshold_sec=60,
            check_interval_sec=15,
        )
        watcher.start()
        ...
        watcher.stop()

    Attributs d'état (lisibles pour debug) :
        last_activity : float    — timestamp dernière activité détectée
        last_action_at : float   — timestamp dernière action déclenchée
        actions_count : int      — nombre d'actions déclenchées
        is_idle : bool           — True si inactif > seuil (instantané)
        idle_seconds : float     — durée d'inactivité actuelle
    """

    def __init__(
        self,
        on_idle=None,
        idle_threshold_sec: float = 60.0,
        check_interval_sec: float = 15.0,
        cooldown_sec: float = 300.0,
        event_bus_path: Optional[Path] = None,
    ):
        """Initialise le watcher.

        Args:
            on_idle: callback appelée avec idle_seconds quand inactif.
                     Doit être non-bloquante (sinon bloque la boucle).
            idle_threshold_sec: secondes d'inactivité avant déclenchement.
            check_interval_sec: fréquence de vérification de l'event_bus.
            cooldown_sec: minimum entre deux actions (anti-thrash).
            event_bus_path: chemin vers event_bus.db (default: memory/event_bus.db).
        """
        self._on_idle = on_idle
        self._threshold = idle_threshold_sec
        self._interval = check_interval_sec
        self._cooldown = cooldown_sec
        self._event_bus_path = (
            event_bus_path or Path(__file__).parent.parent / "memory" / "event_bus.db"
        )
        self._poll_thread: Optional[threading.Thread] = None
        self._stop_event: Optional[threading.Event] = None
        self.last_activity: float = time.time()
        self.last_action_at: float = 0.0
        self.actions_count: int = 0

    # ── API publique ───────────────────────────────────────────────────

    def start(self):
        """Démarre la surveillance en arrière-plan (thread daemon)."""
        if self._poll_thread is not None:
            return
        self._stop_event = threading.Event()
        self.last_activity = self._read_last_activity()
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()

    def stop(self, timeout: float = 3.0):
        """Arrête la surveillance."""
        if self._stop_event is not None:
            self._stop_event.set()
        if self._poll_thread is not None:
            self._poll_thread.join(timeout=timeout)
        self._poll_thread = None
        self._stop_event = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    @property
    def is_alive(self) -> bool:
        """True si le watcher tourne."""
        return self._poll_thread is not None and self._poll_thread.is_alive()

    @property
    def is_idle(self) -> bool:
        """True si l'inactivité actuelle dépasse le seuil."""
        return self.idle_seconds >= self._threshold

    @property
    def idle_seconds(self) -> float:
        """Secondes écoulées depuis la dernière activité."""
        return time.time() - self.last_activity

    # ── Lecture event_bus ───────────────────────────────────────────────

    def _read_last_activity(self) -> float:
        """Lit le timestamp de la dernière activité depuis event_bus.db.

        Returns:
            float: timestamp Unix. now() si DB introuvable ou vide.
        """
        if not self._event_bus_path.exists():
            return time.time()
        try:
            conn = sqlite3.connect(
                f"file:{self._event_bus_path}?mode=ro",
                uri=True,
                timeout=2,
            )
            try:
                row = conn.execute(
                    """SELECT COALESCE(MAX(processed_at), MAX(created_at))
                       FROM events"""
                ).fetchone()
            finally:
                conn.close()
            if row and row[0]:
                return _parse_sqlite_dt(row[0])
            return time.time()
        except Exception:
            return time.time()

    # ── Boucle de polling ───────────────────────────────────────────────

    def _poll_loop(self):
        """Boucle principale du watcher."""
        while not self._stop_event.wait(self._interval):
            try:
                last = self._read_last_activity()
                if last > self.last_activity:
                    self.last_activity = last
                    continue
                if not self.is_idle:
                    continue
                now = time.time()
                if now - self.last_action_at < self._cooldown:
                    continue
                self.last_action_at = now
                self.actions_count += 1
                if self._on_idle is not None:
                    try:
                        self._on_idle(self.idle_seconds)
                    except Exception:
                        pass
            except Exception:
                pass


def _parse_sqlite_dt(value) -> float:
    """Parse un datetime SQLite vers timestamp Unix.

    Supporte 'YYYY-MM-DD HH:MM:SS' et ISO 8601.
    Returns now() si parse échoue.
    """
    if not value:
        return time.time()
    try:
        from datetime import datetime

        s = str(value).replace("T", " ")
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(s, fmt)
                return dt.timestamp()
            except ValueError:
                continue
        return time.time()
    except Exception:
        return time.time()


def start_idle_watcher(
    on_idle=None,
    idle_threshold_sec: float = 60.0,
    cache: Optional[SpiderCache] = None,
) -> IdleWatcher:
    """Démarre l'IdleWatcher (singleton).

    Exemples d'usage:
        # 1. Pré-chauffer le cache pendant l'inactivité
        def warmup(idle_secs):
            cache = get_cache()
            for p in cache.principles:
                _ = p.embedding  # touche la RAM
        start_idle_watcher(on_idle=warmup, idle_threshold_sec=30)

        # 2. Logger seulement
        start_idle_watcher(
            on_idle=lambda s: print(f"[IDLE] {s:.0f}s"),
            idle_threshold_sec=120,
        )
    """
    global _IDLE
    if _IDLE is not None:
        return _IDLE
    _IDLE = IdleWatcher(
        on_idle=on_idle,
        idle_threshold_sec=idle_threshold_sec,
    )
    _IDLE.start()
    return _IDLE
