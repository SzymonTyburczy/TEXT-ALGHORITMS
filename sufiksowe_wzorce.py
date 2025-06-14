import time
import tracemalloc

def search_suffix_array(text: str, pattern: str):
    """
    Przeszukuje `text` za pomocą suffix array + binary search.
    Zwraca:
      - matches: lista pozycji startowych dopasowań
      - metrics: słownik z kluczami:
          'build_time'           – czas budowy tablicy sufiksów,
          'search_time'          – czas wyszukiwania (dwa bin-search),
          'comparisons'          – liczba porównań znaków w fazie wyszukiwania,
          'memory_bytes'         – zużycie pamięci na strukturę (peak_build – peak_base),
          'memory_per_char'      – pamięć na znak tekstu,
          'time_per_pattern_char'– czas wyszukiwania / długość wzorca.
    """
    n, m = len(text), len(pattern)
    total_pat_len = m

    # --- Pomiar pamięci przed buildem ---
    tracemalloc.start()
    base_current, base_peak = tracemalloc.get_traced_memory()

    # --- Budowa suffix array ---
    t0 = time.perf_counter()
    sa = sorted(range(n), key=lambda i: text[i:])  # lista indeksów początków sufiksów
    t1 = time.perf_counter()
    build_time = t1 - t0

    curr_after_build, peak_after_build = tracemalloc.get_traced_memory()

    # --- Przygotowanie do wyszukiwania ---
    comparisons = 0

    def _cmp_suffix(i: int) -> int:
        """
        Porównuje suffix text[i:] z pattern:
          - zwraca -1, jeśli suffix < pattern
          -          0, jeśli prefix=suffix[0:m] == pattern
          -          1, jeśli suffix > pattern
        Zwiększa licznik `comparisons` przy każdym porównaniu znak–znak.
        """
        nonlocal comparisons
        for j in range(m):
            comparisons += 1
            if i + j >= n:
                return -1
            if text[i + j] < pattern[j]:
                return -1
            if text[i + j] > pattern[j]:
                return 1
        return 0

    # --- Wyszukiwanie (dwa bin-search dla [left, right) w sa) ---
    t2 = time.perf_counter()

    # lewy kraniec przedziału dopasowań
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if _cmp_suffix(sa[mid]) < 0:
            lo = mid + 1
        else:
            hi = mid
    left = lo

    # prawy kraniec
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if _cmp_suffix(sa[mid]) <= 0:
            lo = mid + 1
        else:
            hi = mid
    right = lo

    matches = sa[left:right]

    t3 = time.perf_counter()
    search_time = t3 - t2

    # --- Pomiar pamięci po wszystkim ---
    curr_final, peak_final = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    mem_used = peak_after_build - base_peak
    mem_per_char = mem_used / n if n else 0
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

# ---- Przykład użycia ----
if __name__ == "__main__":
    txt = "abracadabra"
    pat = "abra"
    hits, m = search_suffix_array(txt, pat)
    print("Suffix Array → Pozycje:", hits)
    print("                Metryki:", m)
