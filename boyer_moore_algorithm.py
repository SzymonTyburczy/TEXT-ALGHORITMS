import time
import tracemalloc

def search_boyer_moore(text: str, pattern: str):
    """
    Boyer–Moore z heurystyką bad-character i good-suffix.
    Zwraca:
      - matches: lista pozycji startowych
      - metrics: słownik z kluczami:
          'build_time', 'search_time', 'comparisons',
          'memory_bytes', 'memory_per_char', 'time_per_pattern_char'
    """
    m = len(pattern)
    n = len(text)
    total_pat_len = m

    # --- START POMIARU PAMIĘCI ---
    tracemalloc.start()
    base_current, base_peak = tracemalloc.get_traced_memory()

    # --- BUDOWA tabel bad-character i good-suffix ---
    t0 = time.perf_counter()
    # 1) bad-character
    last = {ch: i for i, ch in enumerate(pattern)}
    # 2) good-suffix
    suffix = [-1] * m
    prefix = [False] * m
    for i in range(m - 1):
        j, k = i, 0
        while j >= 0 and pattern[j] == pattern[m - 1 - k]:
            suffix[k + 1] = j
            j -= 1
            k += 1
        if j == -1:
            prefix[k] = True
    t1 = time.perf_counter()
    build_time = t1 - t0

    curr_after_build, peak_after_build = tracemalloc.get_traced_memory()

    # --- PRZESZUKIWANIE ---
    comparisons = 0
    matches = []
    t2 = time.perf_counter()
    i = 0
    while i <= n - m:
        j = m - 1
        # porównujemy od końca
        while j >= 0:
            comparisons += 1
            if pattern[j] != text[i + j]:
                break
            j -= 1
        if j < 0:
            matches.append(i)
            shift = m
        else:
            # bad-character
            bc_shift = j - last.get(text[i + j], -1)
            # good-suffix
            gs_shift = m
            k = m - 1 - j
            if 0 < k and suffix[k] != -1:
                gs_shift = j + 1 - suffix[k]
            else:
                for r in range(j + 2, m):
                    if prefix[m - r]:
                        gs_shift = r
                        break
            shift = max(bc_shift, gs_shift)
        i += shift
    t3 = time.perf_counter()
    search_time = t3 - t2

    # --- STOP POMIARU PAMIĘCI ---
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

# ---- PRZYKŁADOWE UŻYCIE ----
if __name__ == "__main__":
    txt = "abracadabra"
    pat = "abra"
    hits, m = search_boyer_moore(txt, pat)
    print("Boyer–Moore → Pozycje:", hits)
    print("           Metryki:", m)
