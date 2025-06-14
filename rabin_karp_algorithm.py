import time
import tracemalloc

def search_rabin_karp(text: str, pattern: str):
    """
    Rabin–Karp: rolling hash + weryfikacja przy hash-match.
    Zwraca:
      - matches: lista pozycji startowych
      - metrics: słownik z kluczami:
          'build_time', 'search_time', 'comparisons',
          'memory_bytes', 'memory_per_char', 'time_per_pattern_char'
    """
    m = len(pattern)
    n = len(text)
    total_pat_len = m
    base = 256
    mod = 10**9 + 7

    tracemalloc.start()
    base_current, base_peak = tracemalloc.get_traced_memory()

    # --- PREPROCESSING (hash pattern + pierwszy window) ---
    t0 = time.perf_counter()
    pat_hash = 0
    for ch in pattern:
        pat_hash = (pat_hash * base + ord(ch)) % mod
    text_hash = 0
    for i in range(min(m, n)):
        text_hash = (text_hash * base + ord(text[i])) % mod
    h = pow(base, m-1, mod)
    t1 = time.perf_counter()
    build_time = t1 - t0

    curr_after_build, peak_after_build = tracemalloc.get_traced_memory()

    # --- SEARCH ---
    comparisons = 0
    matches = []
    t2 = time.perf_counter()
    for i in range(n - m + 1):
        if text_hash == pat_hash:
            # weryfikujemy znaki
            match = True
            for j in range(m):
                comparisons += 1
                if text[i+j] != pattern[j]:
                    match = False
                    break
            if match:
                matches.append(i)
        # update rolling hash
        if i < n - m:
            text_hash = (text_hash - ord(text[i]) * h) % mod
            text_hash = (text_hash * base + ord(text[i+m])) % mod
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
    hits, m = search_rabin_karp(txt, pat)
    print("Rabin–Karp → Pozycje:", hits)
    print("            Metryki:", m)
