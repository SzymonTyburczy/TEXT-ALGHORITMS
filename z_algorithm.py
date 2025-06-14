import time
import tracemalloc

def search_z(text: str, pattern: str):
    """
    Z-algorytm: łączy pattern+'$'+text, buduje tablicę Z,
    dopasowania tam, gdzie Z[i] == len(pattern).
    Zwraca:
      - matches: lista pozycji startowych
      - metrics: słownik z kluczami:
          'build_time', 'search_time', 'comparisons',
          'memory_bytes', 'memory_per_char', 'time_per_pattern_char'
    """
    m = len(pattern)
    n = len(text)
    total_pat_len = m

    tracemalloc.start()
    base_current, base_peak = tracemalloc.get_traced_memory()

    # brak preprocessing → build_time = 0
    build_time = 0.0
    curr_after_build, peak_after_build = tracemalloc.get_traced_memory()

    comparisons = 0
    matches = []
    t2 = time.perf_counter()

    s = pattern + '$' + text
    L = len(s)
    Z = [0] * L
    l = r = 0
    for i in range(1, L):
        if i > r:
            l = r = i
            while r < L:
                comparisons += 1
                if s[r - l] == s[r]:
                    r += 1
                else:
                    break
            Z[i] = r - l
            r -= 1
        else:
            k = i - l
            if Z[k] < r - i + 1:
                Z[i] = Z[k]
            else:
                l = i
                while r < L:
                    comparisons += 1
                    if s[r - l] == s[r]:
                        r += 1
                    else:
                        break
                Z[i] = r - l
                r -= 1
        if Z[i] == m:
            matches.append(i - m - 1)

    t3 = time.perf_counter()
    search_time = t3 - t2

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
    hits, m = search_z(txt, pat)
    print("Z-algorytm → Pozycje:", hits)
    print("             Metryki:", m)
