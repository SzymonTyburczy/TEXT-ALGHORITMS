import time
import tracemalloc
from collections import deque

class _ACNode:
    __slots__ = ('children', 'fail', 'output')
    def __init__(self):
        self.children = {}
        self.fail = None
        self.output = []

def _build_automaton(patterns):
    root = _ACNode()
    for idx, pat in enumerate(patterns):
        node = root
        for ch in pat:
            node = node.children.setdefault(ch, _ACNode())
        node.output.append((idx, pat))
    q = deque()
    # ustawiamy fail dla dzieci root
    for child in root.children.values():
        child.fail = root
        q.append(child)
    # BFS po drzewie
    while q:
        curr = q.popleft()
        for ch, nxt in curr.children.items():
            q.append(nxt)
            f = curr.fail
            while f and ch not in f.children:
                f = f.fail
            nxt.fail = f.children[ch] if f and ch in f.children else root
            nxt.output += nxt.fail.output
    return root

def search(text: str, patterns: list):
    """
    Przeszukuje `text` pod kątem wszystkich wzorców z listy `patterns`.
    Zwraca:
      - matches: lista (pozycja, (indeks_wzorca, wzorzec))
      - metrics: słownik z kluczami:
          'build_time', 'search_time',
          'comparisons', 'memory_bytes', 'memory_per_char',
          'time_per_pattern_char'
    """
    total_pat_len = sum(len(p) for p in patterns)

    # start pomiaru pamięci
    tracemalloc.start()
    base_current, base_peak = tracemalloc.get_traced_memory()

    # budowa automatu i pomiar czasu
    t0 = time.perf_counter()
    root = _build_automaton(patterns)
    t1 = time.perf_counter()
    build_time = t1 - t0

    curr_after_build, peak_after_build = tracemalloc.get_traced_memory()

    # wyszukiwanie i pomiar czasu + porównań
    comparisons = 0
    matches = []
    node = root

    t2 = time.perf_counter()
    for i, ch in enumerate(text):
        # przejścia fail aż znajdziemy krawędź lub root
        while node and ch not in node.children:
            comparisons += 1
            node = node.fail
        if node:
            comparisons += 1
            node = node.children[ch]
        else:
            node = root
        for match in node.output:
            matches.append((i - len(match[1]) + 1, match))
    t3 = time.perf_counter()
    search_time = t3 - t2

    # końcowy snapshot
    curr_final, peak_final = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    mem_used = peak_after_build - base_peak
    mem_per_char = mem_used / len(text) if text else 0
    time_per_pat_char = search_time / total_pat_len if total_pat_len else 0

    metrics = {
        'build_time': build_time,
        'search_time': search_time,
        'comparisons': comparisons,
        'memory_bytes': mem_used,
        'memory_per_char': mem_per_char,
        'time_per_pattern_char': time_per_pat_char
    }

    return matches, metrics


