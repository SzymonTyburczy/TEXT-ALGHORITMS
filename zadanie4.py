import aho_corasick_algorithm
import boyer_moore_algorithm
import kmp_algorithm
import naive_pattern_matching
import rabin_karp_algorithm
import sufiksowe_wzorce
import z_algorithm

# compare_algorithms.py
"""
Moduł zawierający funkcję do porównania wydajności różnych algorytmów dopasowania wzorca.
"""
import importlib
import time
import tracemalloc

# Lista modułów z algorytmami oraz nazwy funkcji wyszukiwania
ALGOS = [
    ("naive_pattern_matching", "naive_pattern_match"),
    ("kmp_algorithm", "kmp_pattern_match"),
    ("rabin_karp_algorithm", "rabin_karp_pattern_match"),
    ("boyer_moore_algorithm", "boyer_moore_pattern_match"),
    ("z_algorithm", "z_pattern_match"),
    ("sufiksowe_wzorce", "suffix_array_search"),  # algorytm oparty na tablicy sufiksów
    ("aho_corasick_algorithm", "search")  # wyszukiwanie wielu wzorców
]

def compare_pattern_matching_algorithms(text: str, pattern: str) -> dict:
    """
    Porównuje wydajność różnych algorytmów dopasowania wzorca.

    Args:
        text: Tekst, w którym szukamy
        pattern: Wzorzec do znalezienia

    Returns:
        Słownik z wynikami dla każdego algorytmu:
          - time_ms: czas wykonania w milisekundach
          - memory_kb: przyrost zużycia pamięci w kilobajtach
          - comparisons: liczba porównań znaków (jeśli dostępna)
          - positions: lista pozycji, w których wzorzec występuje
    """
    results = {}

    for module_name, func_name in ALGOS:
        try:
            module = importlib.import_module(module_name)
            func = getattr(module, func_name)

            # reset licznika porównań, jeśli zaimplementowany
            if hasattr(module, 'comparisons'):
                module.comparisons = 0

            # monitoruj pamięć
            tracemalloc.start()
            snap_before = tracemalloc.take_snapshot()

            # pomiar czasu
            t0 = time.perf_counter()
            positions = func(text, pattern)
            elapsed_ms = (time.perf_counter() - t0) * 1000

            # snapshot pamięci po wykonaniu
            snap_after = tracemalloc.take_snapshot()
            tracemalloc.stop()

            # oblicz wzrost pamięci w KB
            diff = snap_after.compare_to(snap_before, 'filename')
            mem_bytes = sum(stat.size_diff for stat in diff if stat.size_diff > 0)
            mem_kb = mem_bytes / 1024

            # pobierz liczbę porównań
            comps = getattr(module, 'comparisons', None)

            results[module_name] = {
                'time_ms': elapsed_ms,
                'memory_kb': mem_kb,
                'comparisons': comps,
                'positions': positions
            }
        except Exception as e:
            results[module_name] = {'error': str(e)}

    return results


if __name__ == '__main__':
    # Przykład użycia
    text = "abracadabra" * 10
    pattern = "abra"
    res = compare_pattern_matching_algorithms(text, pattern)
    from pprint import pprint
    pprint(res)
