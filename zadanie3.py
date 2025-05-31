import time
import tracemalloc
import sys

def compare_suffix_structures(text: str) -> dict:
    """
    Compare suffix array and suffix tree data structures.

    Args:
        text: The input text for which to build the structures

    Returns:
        A dictionary containing:
        - Construction time for both structures (ms)
        - Memory usage for both structures (KB)
        - Size (number of nodes/elements) of both structures
    """

    ### 1) Suffix Array #####################################################
    def build_suffix_array(s: str):
        """Najprostsza implementacja: sortujemy wszystkie sufiksy."""
        return sorted(range(len(s)), key=lambda i: s[i:])

    # Pomiar czasu i pamięci dla tablicy sufiksów
    tracemalloc.start()
    t0 = time.perf_counter()
    sa = build_suffix_array(text)
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    sa_time_ms = (t1 - t0) * 1000
    sa_mem_kb = peak / 1024
    sa_size = len(sa)


    ### 2) Suffix Tree (Ukkonen) ##############################################
    class SuffixTreeNode:
        def __init__(self, start, end):
            self.children = {}      # map: char -> SuffixTreeNode
            self.suffix_link = None
            self.start = start
            self.end = end          # może być int albo referencja do leaf_end

    class SuffixTree:
        def __init__(self, data):
            self.data = data
            self.root = SuffixTreeNode(-1, -1)
            self.root.suffix_link = self.root
            self.size = len(data)
            self.build()

        def edge_length(self, node):
            return (node.end[0] if isinstance(node.end, list) else node.end) - node.start + 1

        def build(self):
            s = self.data
            self.leaf_end = [ -1 ]     # używamy listy, żeby referencja się zmieniała
            self.remaining = 0
            self.active_node = self.root
            self.active_edge = -1
            self.active_length = 0
            self.last_new_node = None

            # funkcja pomocnicza do test-and-split + update
            def extend(pos):
                self.leaf_end[0] = pos
                self.remaining += 1
                self.last_new_node = None

                while self.remaining > 0:
                    if self.active_length == 0:
                        self.active_edge = pos
                    ch = s[self.active_edge]
                    # jeżeli nie ma takiego dziecka
                    if ch not in self.active_node.children:
                        # stwórz nowy liść
                        leaf = SuffixTreeNode(pos, self.leaf_end)
                        self.active_node.children[ch] = leaf
                        # linki sufiksowe
                        if self.last_new_node:
                            self.last_new_node.suffix_link = self.active_node
                            self.last_new_node = None
                    else:
                        nxt = self.active_node.children[ch]
                        if self.active_length >= self.edge_length(nxt):
                            self.active_edge += self.edge_length(nxt)
                            self.active_length -= self.edge_length(nxt)
                            self.active_node = nxt
                            continue
                        # jeżeli znak pasuje – Extension Rule 3 (nie tworzymy nowego węzła)
                        if s[nxt.start + self.active_length] == s[pos]:
                            if self.last_new_node and self.active_node != self.root:
                                self.last_new_node.suffix_link = self.active_node
                                self.last_new_node = None
                            self.active_length += 1
                            break
                        # trzeba rozdzielić krawędź – Extension Rule 2
                        split_end = [nxt.start + self.active_length - 1]
                        split = SuffixTreeNode(nxt.start, split_end)
                        self.active_node.children[ch] = split
                        # nowy liść
                        leaf = SuffixTreeNode(pos, self.leaf_end)
                        split.children[s[pos]] = leaf
                        nxt.start += self.active_length
                        split.children[s[nxt.start]] = nxt

                        if self.last_new_node:
                            self.last_new_node.suffix_link = split
                        self.last_new_node = split

                    self.remaining -= 1
                    if self.active_node == self.root and self.active_length > 0:
                        self.active_length -= 1
                        self.active_edge = pos - self.remaining + 1
                    elif self.active_node != self.root:
                        self.active_node = self.active_node.suffix_link

            # buduj drzewo
            for i in range(len(s)):
                extend(i)

        def count_nodes(self):
            """Zlicz wszystkie węzły w drzewie."""
            cnt = 0
            stack = [self.root]
            while stack:
                node = stack.pop()
                cnt += 1
                for child in node.children.values():
                    stack.append(child)
            return cnt

    # Pomiar czasu i pamięci dla drzewa sufiksów
    tracemalloc.start()
    t0 = time.perf_counter()
    st = SuffixTree(text)
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    st_time_ms = (t1 - t0) * 1000
    st_mem_kb = peak / 1024
    st_size = st.count_nodes()


    return {
        "suffix_array": {
            "construction_time_ms": sa_time_ms,
            "memory_usage_kb": sa_mem_kb,
            "size": sa_size
        },
        "suffix_tree": {
            "construction_time_ms": st_time_ms,
            "memory_usage_kb": st_mem_kb,
            "size": st_size
        }
    }
result = compare_suffix_structures("bananabanaba$")
print(result)
