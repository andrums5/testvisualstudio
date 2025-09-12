"""
Script de demostración con varias herramientas útiles en un solo archivo.

Subcomandos disponibles:
  - text:    Analiza texto y muestra palabras más frecuentes.
  - stats:   Calcula estadísticas descriptivas y un histograma ASCII.
  - path:    Calcula rutas más cortas en un grafo (Dijkstra/BFS).
  - async:   Demostración de concurrencia con asyncio.
  - cache:   Demostración de aceleración con lru_cache (Fibonacci).
  - doctest: Ejecuta doctests embebidos.
  - live:    Demo visual con barra de progreso y spinner.

Ejemplos rápidos:
  python test.py text "Hola hola mundo, mundo mundo!" --top 2
  python test.py stats 1 2 3 4 5 --bins 5
  python test.py path --edges "A-B:3,B-C:4,A-C:10" --start A --end C
  python test.py async 0.6 0.3 0.2 0.5
  python test.py cache 35
  python test.py doctest
"""

from __future__ import annotations

import argparse
import asyncio
import collections
import dataclasses
import functools
import heapq
import json
import math
import random
import statistics
import sys
import time
import unicodedata
from typing import Dict, Iterable, List, Sequence, Tuple


# -------------------------- Utilidades generales ---------------------------

def _normalize_text(s: str) -> str:
    """Normaliza a minúsculas y quita tildes.

    >>> _normalize_text("Café Niño")
    'cafe nino'
    """
    s = s.lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s


def _tokenize(s: str) -> List[str]:
    """Divide texto en tokens alfabéticos (incluyendo letras acentuadas normalizadas).

    >>> _tokenize("Hola, mundo! Hola...")
    ['hola', 'mundo', 'hola']
    """
    import re

    s = _normalize_text(s)
    # Palabras de 2+ letras (ignora números/guiones/puntuación)
    return re.findall(r"[a-zA-Záéíóúñü]{2,}", s)


EN_STOPWORDS = {
    "the",
    "and",
    "a",
    "an",
    "in",
    "on",
    "for",
    "of",
    "to",
    "is",
    "it",
    "that",
    "with",
    "as",
    "at",
    "by",
    "be",
    "this",
    "from",
    "or",
}

ES_STOPWORDS = {
    "el",
    "la",
    "los",
    "las",
    "y",
    "o",
    "de",
    "del",
    "en",
    "un",
    "una",
    "es",
    "que",
    "con",
    "por",
    "para",
    "se",
    "al",
    "lo",
    "a",
}


def analyze_text(text: str, top: int = 10, lang: str = "auto") -> Dict[str, object]:
    """Analiza texto y devuelve estadísticas básicas.

    - Tokeniza y normaliza
    - Elimina stopwords (es/en o mixto si auto)
    - Devuelve top-N palabras con frecuencias y conteos totales

    >>> res = analyze_text("Hola hola mundo, mundo mundo!", top=2, lang="es")
    >>> [w for w, _ in res['top_words']]
    ['mundo', 'hola']
    >>> res['total_tokens']
    5
    """
    tokens = _tokenize(text)
    if lang == "es":
        stop = ES_STOPWORDS
    elif lang == "en":
        stop = EN_STOPWORDS
    else:  # auto -> union simple
        stop = ES_STOPWORDS | EN_STOPWORDS

    filtered = [t for t in tokens if t not in stop]
    counter = collections.Counter(filtered)
    top_words = counter.most_common(top)

    return {
        "total_tokens": len(tokens),
        "total_filtered": len(filtered),
        "unique_words": len(counter),
        "top_words": top_words,
    }


# ------------------------------ Estadísticas -------------------------------

@dataclasses.dataclass
class Stats:
    count: int
    mean: float
    median: float
    stdev: float | None
    minimum: float
    maximum: float
    p25: float
    p75: float
    iqr: float
    sum: float


def describe(numbers: Sequence[float]) -> Stats:
    """Calcula estadísticas descriptivas robustas.

    >>> s = describe([1, 2, 2, 3, 4])
    >>> (s.count, round(s.mean, 2), s.minimum, s.maximum)
    (5, 2.4, 1.0, 4.0)
    """
    if not numbers:
        raise ValueError("No hay números para describir")

    nums = list(map(float, numbers))
    nums.sort()
    count = len(nums)
    mean = statistics.fmean(nums)
    median = statistics.median(nums)
    stdev = statistics.stdev(nums) if count >= 2 else None
    minimum = nums[0]
    maximum = nums[-1]

    def percentile(p: float) -> float:
        if not 0 <= p <= 1:
            raise ValueError("Percentil fuera de rango")
        k = (len(nums) - 1) * p
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return nums[int(k)]
        return nums[f] * (c - k) + nums[c] * (k - f)

    p25 = percentile(0.25)
    p75 = percentile(0.75)
    iqr = p75 - p25

    return Stats(
        count=count,
        mean=mean,
        median=median,
        stdev=stdev,
        minimum=minimum,
        maximum=maximum,
        p25=p25,
        p75=p75,
        iqr=iqr,
        sum=float(sum(nums)),
    )


def ascii_histogram(numbers: Sequence[float], bins: int = 10, width: int = 40) -> str:
    """Genera un histograma ASCII.

    >>> print(ascii_histogram([1,1,2,2,2,3,5,8], bins=4, width=10))
    [1.00,2.75) | ##########
    [2.75,4.50) | ##
    [4.50,6.25) | ##
    [6.25,8.00] | ##
    """
    if not numbers:
        return "(sin datos)"
    data = list(map(float, numbers))
    lo, hi = min(data), max(data)
    if lo == hi:
        return f"[{lo:.2f},{hi:.2f}] | " + "#" * width

    step = (hi - lo) / bins
    edges = [lo + i * step for i in range(bins)] + [hi]
    counts = [0] * bins
    for x in data:
        if x == hi:
            counts[-1] += 1
        else:
            idx = int((x - lo) / step)
            counts[idx] += 1

    maxc = max(counts) or 1
    lines = []
    for i, c in enumerate(counts):
        a = edges[i]
        b = edges[i + 1]
        bar = "#" * max(1, round(c / maxc * width)) if c else ""
        clos = "]" if i == bins - 1 else ")"
        lines.append(f"[{a:.2f},{b:.2f}{clos} | {bar}")
    return "\n".join(lines)


# --------------------------------- Grafos ----------------------------------

Graph = Dict[str, Dict[str, float]]


def parse_edges(spec: str, undirected: bool = True) -> Graph:
    """Parses edges like "A-B:3,B-C:4,A-C:10" into an adjacency dict.

    >>> parse_edges("A-B:2,B-C:1")['A']['B']
    2.0
    """
    graph: Graph = collections.defaultdict(dict)
    if not spec:
        return graph
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            nodes, weight = part.split(":")
            a, b = nodes.split("-")
            w = float(weight)
        except ValueError as e:
            raise ValueError(f"Formato de arista inválido: '{part}'") from e
        graph[a][b] = w
        if undirected:
            graph[b][a] = w
    return dict(graph)


def dijkstra(graph: Graph, start: str, end: str) -> Tuple[float, List[str]]:
    """Ruta más corta con Dijkstra.

    >>> g = parse_edges("A-B:3,B-C:4,A-C:10")
    >>> dist, path = dijkstra(g, 'A', 'C')
    >>> (dist, path)
    (7.0, ['A', 'B', 'C'])
    """
    if start not in graph or end not in graph:
        raise ValueError("Nodo inicial o final no existe en el grafo")

    dist = {start: 0.0}
    prev: Dict[str, str | None] = {start: None}
    pq = [(0.0, start)]
    visited: set[str] = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        if u == end:
            break
        for v, w in graph.get(u, {}).items():
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if end not in dist:
        raise ValueError("No hay ruta entre los nodos dados")

    # Reconstruye camino
    path = []
    cur: str | None = end
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return dist[end], path


def bfs_shortest_path(graph: Graph, start: str, end: str) -> List[str]:
    """Camino más corto en grafo no ponderado (BFS)."""
    if start not in graph or end not in graph:
        raise ValueError("Nodo inicial o final no existe en el grafo")
    q = collections.deque([start])
    prev: Dict[str, str | None] = {start: None}
    while q:
        u = q.popleft()
        if u == end:
            break
        for v in graph.get(u, {}):
            if v not in prev:
                prev[v] = u
                q.append(v)
    if end not in prev:
        raise ValueError("No hay ruta entre los nodos dados")
    path = []
    cur: str | None = end
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return list(reversed(path))


# ----------------------------- Async y cache -------------------------------

async def _sleep_task(delay: float, idx: int) -> Tuple[int, float]:
    start = time.perf_counter()
    await asyncio.sleep(delay)
    elapsed = time.perf_counter() - start
    return idx, elapsed


async def run_async_demo(delays: Sequence[float]) -> Dict[str, object]:
    """Ejecuta tareas en paralelo y mide tiempos agregados.

    >>> res = asyncio.run(run_async_demo([0.05, 0.03]))
    >>> 'wall_time' in res and 'per_task' in res
    True
    """
    t0 = time.perf_counter()
    results = await asyncio.gather(*(_sleep_task(d, i) for i, d in enumerate(delays)))
    wall = time.perf_counter() - t0
    per_task = {i: round(el, 4) for i, el in results}
    return {"wall_time": wall, "per_task": per_task}


@functools.lru_cache(maxsize=None)
def fib(n: int) -> int:
    """Fibonacci con cache. Acepta n >= 0.

    >>> fib(10)
    55
    """
    if n < 0:
        raise ValueError("n debe ser >= 0")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_demo(n: int) -> Dict[str, object]:
    """Compara tiempos con/ sin caché para fib(n)."""
    # Limpia cache para medir "primer cálculo"
    fib.cache_clear()
    t0 = time.perf_counter()
    first = fib(n)
    t1 = time.perf_counter() - t0
    # Repite para medir golpe de caché
    t2 = time.perf_counter()
    second = fib(n)
    t3 = time.perf_counter() - t2
    assert first == second
    return {"n": n, "value": first, "first_s": t1, "cached_s": t3}


# -------------------------- Demo visual en vivo ----------------------------

def live_demo(seconds: float = 5.0, width: int = 30) -> None:
    """Muestra una barra de progreso y un spinner animados en stdout.

    Nota: en esta interfaz la salida puede aparecer al final; en tu terminal
    local se animará en tiempo real.
    """
    frames = "|/-\\"
    steps = max(1, int(seconds * 20))  # ~20 FPS
    start = time.perf_counter()
    for i in range(steps + 1):
        pct = i / steps
        filled = int(pct * width)
        bar = "#" * filled + "-" * (width - filled)
        spinner = frames[i % len(frames)]
        elapsed = time.perf_counter() - start
        eta = max(0.0, seconds - elapsed)
        line = f"\r{spinner} [{bar}] {pct:6.2%}  t={elapsed:4.1f}s  eta={eta:4.1f}s"
        sys.stdout.write(line)
        sys.stdout.flush()
        time.sleep(seconds / steps)
    sys.stdout.write("\nCompletado.\n")
    sys.stdout.flush()


# --------------------------------- CLI -------------------------------------

def cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Herramientas de demostración")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # text
    p_text = sub.add_parser("text", help="Analiza texto y muestra top de palabras")
    p_text.add_argument("text", help="Texto a analizar entre comillas")
    p_text.add_argument("--top", type=int, default=10, help="Número de palabras a mostrar")
    p_text.add_argument("--lang", choices=["auto", "es", "en"], default="auto", help="Stopwords a usar")

    # stats
    p_stats = sub.add_parser("stats", help="Estadísticas descriptivas de números")
    p_stats.add_argument("numbers", nargs="*", help="Números separados por espacio")
    p_stats.add_argument("--file", help="Archivo con un número por línea", default=None)
    p_stats.add_argument("--bins", type=int, default=10, help="Número de bins del histograma")
    p_stats.add_argument("--json", action="store_true", help="Salida en JSON")

    # path
    p_path = sub.add_parser("path", help="Ruta más corta en un grafo")
    p_path.add_argument("--edges", required=True, help="Formato A-B:3,B-C:4 ...")
    p_path.add_argument("--start", required=True, help="Nodo inicio")
    p_path.add_argument("--end", required=True, help="Nodo fin")
    p_path.add_argument("--unweighted", action="store_true", help="Usar BFS (no ponderado)")

    # async
    p_async = sub.add_parser("async", help="Demostración de tareas concurrentes")
    p_async.add_argument("delays", nargs="+", type=float, help="Segundos de cada tarea")

    # cache
    p_cache = sub.add_parser("cache", help="Demostración de lru_cache con Fibonacci")
    p_cache.add_argument("n", type=int, help="n para Fibonacci")

    # doctest
    sub.add_parser("doctest", help="Ejecuta doctests embebidos")

    # live
    p_live = sub.add_parser("live", help="Demostración visual con barra de progreso")
    p_live.add_argument("--seconds", type=float, default=5.0, help="Duración de la animación")
    p_live.add_argument("--width", type=int, default=30, help="Ancho de la barra")

    args = parser.parse_args(argv)

    if args.cmd == "text":
        res = analyze_text(args.text, top=args.top, lang=args.lang)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "stats":
        nums: List[float] = []
        if args.file:
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            nums.append(float(line))
            except OSError as e:
                print(f"Error leyendo archivo: {e}", file=sys.stderr)
                return 2
        if args.numbers:
            try:
                nums.extend(float(x) for x in args.numbers)
            except ValueError:
                print("Los valores deben ser numéricos", file=sys.stderr)
                return 2
        if not nums:
            print("Proporciona números o --file", file=sys.stderr)
            return 2
        s = describe(nums)
        hist = ascii_histogram(nums, bins=max(1, args.bins))
        if args.json:
            print(
                json.dumps(
                    dataclasses.asdict(s) | {"histogram": hist}, ensure_ascii=False, indent=2
                )
            )
        else:
            print("Estadísticas:")
            print(f"  count : {s.count}")
            print(f"  mean  : {s.mean:.6g}")
            print(f"  median: {s.median:.6g}")
            if s.stdev is not None:
                print(f"  stdev : {s.stdev:.6g}")
            print(f"  min   : {s.minimum:.6g}")
            print(f"  max   : {s.maximum:.6g}")
            print(f"  p25   : {s.p25:.6g}")
            print(f"  p75   : {s.p75:.6g}")
            print(f"  iqr   : {s.iqr:.6g}")
            print(f"  sum   : {s.sum:.6g}")
            print()
            print("Histograma:")
            print(hist)
        return 0

    if args.cmd == "path":
        try:
            g = parse_edges(args.edges)
            if args.unweighted:
                path = bfs_shortest_path(g, args.start, args.end)
                print(json.dumps({"path": path}, ensure_ascii=False, indent=2))
            else:
                dist, path = dijkstra(g, args.start, args.end)
                print(json.dumps({"distance": dist, "path": path}, ensure_ascii=False, indent=2))
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 2
        return 0

    if args.cmd == "async":
        res = asyncio.run(run_async_demo(args.delays))
        # Redondeo de wall_time para legibilidad
        res["wall_time"] = round(float(res["wall_time"]), 4)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "cache":
        if args.n < 0:
            print("n debe ser >= 0", file=sys.stderr)
            return 2
        res = fib_demo(args.n)
        res = {k: (round(v, 6) if isinstance(v, float) else v) for k, v in res.items()}
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "doctest":
        import doctest

        failures, _ = doctest.testmod()
        return 1 if failures else 0

    if args.cmd == "live":
        # Fuerza buffer lineal si es posible (Python 3.7+)
        try:
            sys.stdout.reconfigure(line_buffering=True)
        except Exception:
            pass
        live_demo(seconds=args.seconds, width=max(10, args.width))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
bcbcnv
