import time
import tracemalloc

def search_kmp(text: str, pattern: str):
    """
    KMP: najpierw liczymy tablicę LPS (longest proper prefix-suffix),
    potem jednoprzebiegowe przeszukiwanie.
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

    # --- BUDOWA (liczenie LPS) ---
    t0 = time.perf_counter()
    # przygotowanie LPS
    lps = [0] * total_pat_len
    length = 0
    i = 1
    while i < total_pat_len:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    t1 = time.perf_counter()
    build_time = t1 - t0

    curr_after_build, peak_after_build = tracemalloc.get_traced_memory()

    # --- PRZESZUKIWANIE + LICZNIK PORÓWNAŃ ---
    comparisons = 0
    matches = []
    n, m = len(text), total_pat_len
    t2 = time.perf_counter()

    ti = 0  # indeks w text
    pj = 0  # indeks w pattern
    while ti < n:
        comparisons += 1
        if text[ti] == pattern[pj]:
            ti += 1
            pj += 1
            if pj == m:
                matches.append(ti - pj)
                pj = lps[pj - 1]
        else:
            if pj:
                pj = lps[pj - 1]
            else:
                ti += 1

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
    hits, m = search_kmp(txt, pat)
    print("Pozycje:", hits)
    print("Metryki:", m)
