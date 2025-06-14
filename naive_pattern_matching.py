import time
import tracemalloc

def search_naive(text: str, pattern: str):
    """
    Naiwne przeszukiwanie: dla każdej pozycji w text sprawdzamy
    kolejno wszystkie znaki pattern.
    Zwraca:
      - matches: lista pozycji startowych
      - metrics: słownik z kluczami:
          'build_time', 'search_time',
          'comparisons', 'memory_bytes', 'memory_per_char',
          'time_per_pattern_char'
    """
    total_pat_len = len(pattern)

    # --- START POMIARU PAMIĘCI ---
    tracemalloc.start()
    base_current, base_peak = tracemalloc.get_traced_memory()

    # --- BUDOWA (brak preprocessing) ---
    t0 = time.perf_counter()
    # (tu nic nie robimy)
    t1 = time.perf_counter()
    build_time = t1 - t0

    curr_after_build, peak_after_build = tracemalloc.get_traced_memory()

    # --- PRZESZUKIWANIE + LICZNIK PORÓWNAŃ ---
    comparisons = 0
    matches = []
    n, m = len(text), len(pattern)

    t2 = time.perf_counter()
    for i in range(n - m + 1):
        for j in range(m):
            comparisons += 1
            if text[i + j] != pattern[j]:
                break
        else:
            matches.append(i)
    t3 = time.perf_counter()
    search_time = t3 - t2

    # --- KONIEC POMIARU PAMIĘCI ---
    curr_final, peak_final = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # --- OBLICZENIE METRYK ---
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

# ---- PRZYKŁAD UŻYCIA ----
if __name__ == "__main__":
    txt = "abracadabra"
    pat = "abra"
    hits, m = search_naive(txt, pat)
    print("Pozycje:", hits)
    print("Metryki:", m)
