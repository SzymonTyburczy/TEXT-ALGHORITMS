import time
import tracemalloc

class _SuffixTreeNode:
    __slots__ = ('children', 'suffix_link', 'start', 'end', 'index')
    def __init__(self, start=None, end=None):
        self.children = {}          # map from character to node
        self.suffix_link = None
        self.start = start          # edge start index
        self.end = end              # edge end index (object with .value for leaves)
        self.index = -1             # for leaves: the suffix start position

class _End:
    __slots__ = ('value',)
    def __init__(self, value):
        self.value = value

def _build_ukkonen_tree(text: str):
    """
    Ukkonen's online algorithm for suffix-tree in O(n).
    Returns root of the tree.
    """
    root = _SuffixTreeNode()
    root.suffix_link = root
    active_node = root
    active_edge = -1
    active_length = 0
    remainder = 0
    end = _End(-1)

    def edge_length(node):
        return node.end.value - node.start + 1

    for pos, ch in enumerate(text):
        end.value = pos
        remainder += 1
        last_new_node = None
        while remainder > 0:
            if active_length == 0:
                active_edge = pos
            edge_char = text[active_edge]
            # if no edge starting with edge_char
            if edge_char not in active_node.children:
                # new leaf
                leaf = _SuffixTreeNode(pos, end)
                leaf.index = pos - remainder + 1
                active_node.children[edge_char] = leaf
                if last_new_node:
                    last_new_node.suffix_link = active_node
                    last_new_node = None
            else:
                next_node = active_node.children[edge_char]
                if active_length >= edge_length(next_node):
                    active_edge += edge_length(next_node)
                    active_length -= edge_length(next_node)
                    active_node = next_node
                    continue
                # character on edge
                if text[next_node.start + active_length] == ch:
                    active_length += 1
                    if last_new_node:
                        last_new_node.suffix_link = active_node
                        last_new_node = None
                    break
                # split edge
                split_end = next_node.start + active_length - 1
                split = _SuffixTreeNode(next_node.start, _End(split_end))
                active_node.children[edge_char] = split
                leaf = _SuffixTreeNode(pos, end)
                leaf.index = pos - remainder + 1
                split.children[ch] = leaf
                next_node.start = split_end + 1
                split.children[text[next_node.start]] = next_node
                if last_new_node:
                    last_new_node.suffix_link = split
                last_new_node = split
            remainder -= 1
            if active_node is root and active_length > 0:
                active_length -= 1
                active_edge = pos - remainder + 1
            else:
                active_node = active_node.suffix_link if active_node.suffix_link else root
    return root

def search_ukkonen(text: str, pattern: str):
    """
    Wyszukiwanie wzorca w tekście za pomocą suffix tree zbudowanego algorytmem Ukkonena.
    Zwraca:
      - matches: lista pozycji startowych wystąpień
      - metrics: słownik jak w pozostałych implementacjach
    """
    n, m = len(text), len(pattern)
    total_pat_len = m

    # --- Pomiar pamięci przed budową ---
    tracemalloc.start()
    base_current, base_peak = tracemalloc.get_traced_memory()

    # --- Budowa drzewa ---
    t0 = time.perf_counter()
    root = _build_ukkonen_tree(text)
    t1 = time.perf_counter()
    build_time = t1 - t0

    curr_after_build, peak_after_build = tracemalloc.get_traced_memory()

    # --- Przeszukiwanie w drzewie ---
    comparisons = 0
    t2 = time.perf_counter()
    node = root
    i = 0
    # schodzimy po krawędziach zgodnie ze wzorcem
    while i < m:
        ch = pattern[i]
        if ch not in node.children:
            comparisons += 1
            # brak krawędzi → brak dopasowania
            search_time = time.perf_counter() - t2
            mem_used = peak_after_build - base_peak
            metrics = {
                'build_time': build_time,
                'search_time': search_time,
                'comparisons': comparisons,
                'memory_bytes': mem_used,
                'memory_per_char': mem_used / n if n else 0,
                'time_per_pattern_char': search_time / total_pat_len if total_pat_len else 0
            }
            return [], metrics
        edge = node.children[ch]
        length = edge.end.value - edge.start + 1
        # porównania znak po znaku na krawędzi
        for k in range(length):
            comparisons += 1
            if i + k >= m or text[edge.start + k] != pattern[i + k]:
                search_time = time.perf_counter() - t2
                mem_used = peak_after_build - base_peak
                metrics = {
                    'build_time': build_time,
                    'search_time': search_time,
                    'comparisons': comparisons,
                    'memory_bytes': mem_used,
                    'memory_per_char': mem_used / n if n else 0,
                    'time_per_pattern_char': search_time / total_pat_len if total_pat_len else 0
                }
                return [], metrics
        # całe segment pasuje → schodzimy
        node = edge
        i += length

    # jeśli wzorzec w drzewie, zbieramy wszystkie sufiksy w poddrzewie
    matches = []
    stack = [node]
    while stack:
        u = stack.pop()
        if u.index >= 0:
            matches.append(u.index)
        for child in u.children.values():
            stack.append(child)
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

    return sorted(matches), metrics

# ---- Przykład użycia ----
if __name__ == "__main__":
    txt = "bananabanaba$"
    pat = "ana"
    hits, m = search_ukkonen(txt, pat)
    print("Ukkonen → Pozycje:", hits)
    print("          Metryki:", m)
