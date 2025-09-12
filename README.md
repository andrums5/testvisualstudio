# Proyecto de demo (test.py)

Este repositorio contiene un script multi‑herramienta en `test.py` con subcomandos:

- `text`: análisis de texto y top‑N de palabras.
- `stats`: estadísticas descriptivas y histograma ASCII.
- `path`: rutas más cortas (Dijkstra/BFS) en un grafo simple.
- `async`: demostración de concurrencia con `asyncio`.
- `cache`: demostración de `lru_cache` con Fibonacci.
- `doctest`: ejecuta los doctests embebidos.
 - `live`: demo visual con barra de progreso y spinner.

## Uso rápido

```bash
python test.py -h
python test.py text "Hola hola mundo, mundo mundo!" --top 2
python test.py stats --file datasets/numbers.txt --bins 5
python test.py path --edges "A-B:3,B-C:4,A-C:10" --start A --end C
python test.py async 0.2 0.1 0.05
python test.py cache 35
python test.py doctest
python test.py live --seconds 6 --width 40
```

## Scripts

- `scripts/run_examples.py`: ejecuta una serie de ejemplos y muestra su salida.
