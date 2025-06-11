import time
import tracemalloc
import random
import string
import matplotlib.pyplot as plt

# -------------------------
# Suffix Array implementation (Doubling algorithm)
# -------------------------
class SuffixArray:
    def __init__(self, text):
        self.text = text
        self.sa = self.build_sa()

    def build_sa(self):
        s = self.text
        n = len(s)
        k = 1
        rank = [ord(c) for c in s]
        tmp = [0] * n
        sa = list(range(n))
        while True:
            sa.sort(key=lambda x: (rank[x], rank[x+k] if x+k < n else -1))
            tmp[sa[0]] = 0
            for i in range(1, n):
                prev, curr = sa[i-1], sa[i]
                prev_key = (rank[prev], rank[prev+k] if prev+k < n else -1)
                curr_key = (rank[curr], rank[curr+k] if curr+k < n else -1)
                tmp[curr] = tmp[prev] + (prev_key < curr_key)
            rank, tmp = tmp, rank
            k <<= 1
            if rank[sa[-1]] == n - 1:
                break
        return sa

# -------------------------
# Suffix Tree using Ukkonen's algorithm
# -------------------------
class SuffixTreeNode:
    def __init__(self):
        self.children = {}
        self.suffix_link = None
        self.start = -1
        self.end = -1

class SuffixTree:
    def __init__(self, text):
        self.text = text
        self.size = len(text)
        # Create root
        root = SuffixTreeNode()
        root.start = -1
        root.end = -1
        root.suffix_link = root
        self.root = root
        self.active_node = self.root
        self.active_edge = -1
        self.active_length = 0
        self.remaining = 0
        self.leaf_end = -1
        self.last_new_node = None
        for i in range(self.size):
            self._extend(i)

    def new_node(self, start, end):
        node = SuffixTreeNode()
        node.start = start
        node.end = end
        node.suffix_link = self.root  # default suffix link to root
        return node

    def _edge_length(self, node):
        return ((node.end if node.end != -1 else self.leaf_end) - node.start + 1)

    def _walk_down(self, node):
        length = self._edge_length(node)
        if self.active_length >= length:
            self.active_edge += length
            self.active_length -= length
            self.active_node = node
            return True
        return False

    def _extend(self, pos):
        self.leaf_end = pos
        self.remaining += 1
        self.last_new_node = None

        while self.remaining > 0:
            if self.active_length == 0:
                self.active_edge = pos
            ch = self.text[self.active_edge]
            if ch not in self.active_node.children:
                # Create new leaf node
                leaf = SuffixTreeNode()
                leaf.start = pos
                leaf.end = -1
                leaf.suffix_link = self.root
                self.active_node.children[ch] = leaf
                if self.last_new_node:
                    self.last_new_node.suffix_link = self.active_node
                    self.last_new_node = None
            else:
                next_node = self.active_node.children[ch]
                if self._walk_down(next_node):
                    continue
                if self.text[next_node.start + self.active_length] == self.text[pos]:
                    if self.last_new_node and self.active_node != self.root:
                        self.last_new_node.suffix_link = self.active_node
                        self.last_new_node = None
                    self.active_length += 1
                    break
                # Split edge
                split = self.new_node(next_node.start, next_node.start + self.active_length - 1)
                self.active_node.children[ch] = split
                # New leaf from split
                leaf = SuffixTreeNode()
                leaf.start = pos
                leaf.end = -1
                leaf.suffix_link = self.root
                split.children[self.text[pos]] = leaf
                # Adjust next_node
                next_node.start += self.active_length
                split.children[self.text[next_node.start]] = next_node
                if self.last_new_node:
                    self.last_new_node.suffix_link = split
                self.last_new_node = split
            self.remaining -= 1
            if self.active_node == self.root and self.active_length > 0:
                self.active_length -= 1
                self.active_edge = pos - self.remaining + 1
            elif self.active_node != self.root:
                self.active_node = self.active_node.suffix_link

# Count total nodes in suffix tree
def count_nodes(node):
    total = 1
    for child in node.children.values():
        total += count_nodes(child)
    return total

# Measure performance metrics
def measure(text):
    # Suffix Array
    tracemalloc.start()
    t0 = time.perf_counter()
    sa = SuffixArray(text)
    t1 = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    time_sa = (t1 - t0) * 1000  # ms
    mem_sa = peak / 1024        # KB
    size_sa = len(sa.sa)

    # Suffix Tree
    tracemalloc.start()
    t0 = time.perf_counter()
    st = SuffixTree(text)
    t1 = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    time_st = (t1 - t0) * 1000  # ms
    mem_st = peak / 1024        # KB
    size_st = count_nodes(st.root)

    return time_sa, mem_sa, size_sa, time_st, mem_st, size_st

# Test on increasing text sizes
sizes = [100, 1000, 10000, 100000]
time_sa_list, mem_sa_list, size_sa_list = [], [], []
time_st_list, mem_st_list, size_st_list = [], [], []

for n in sizes:
    text = ''.join(random.choices(string.ascii_lowercase, k=n))
    t_sa, m_sa, s_sa, t_st, m_st, s_st = measure(text)
    time_sa_list.append(t_sa)
    mem_sa_list.append(m_sa)
    size_sa_list.append(s_sa)
    time_st_list.append(t_st)
    mem_st_list.append(m_st)
    size_st_list.append(s_st)

# Plot: Construction Time vs Text Size (log-log)
plt.figure()
plt.plot(sizes, time_sa_list, marker='o', label='Suffix Array')
plt.plot(sizes, time_st_list, marker='o', label='Suffix Tree')
plt.xscale('log'); plt.yscale('log')
plt.xlabel('Text Size (n)')
plt.ylabel('Construction Time (ms)')
plt.legend()
plt.title('Construction Time vs Text Size')
plt.show()

# Plot: Memory Usage vs Text Size (log-log)
plt.figure()
plt.plot(sizes, mem_sa_list, marker='o', label='Suffix Array')
plt.plot(sizes, mem_st_list, marker='o', label='Suffix Tree')
plt.xscale('log'); plt.yscale('log')
plt.xlabel('Text Size (n)')
plt.ylabel('Memory Usage (KB)')
plt.legend()
plt.title('Memory Usage vs Text Size')
plt.show()

# Plot: Structure Size vs Text Size (linear)
plt.figure()
plt.plot(sizes, size_sa_list, marker='o', label='Suffix Array')
plt.plot(sizes, size_st_list, marker='o', label='Suffix Tree')
plt.xlabel('Text Size (n)')
plt.ylabel('Structure Size (# elements/nodes)')
plt.legend()
plt.title('Structure Size vs Text Size')
plt.show()
