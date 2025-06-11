import random
import string
import pandas as pd

# Reusing previously defined LCS functions
def lcs_dp_substr(s1, s2):
    n, m = len(s1), len(s2)
    dp = [[0]*(m+1) for _ in range(n+1)]
    best = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                best = max(best, dp[i][j])
            # else: dp[i][j] = 0  (już jest zero inicjalnie)
    return best


def build_sa(s):
    n = len(s)
    k = 1
    rank = [ord(c) for c in s] + [-1]
    sa = list(range(n))
    tmp = [0]*n
    while k < n:
        sa.sort(key=lambda i: (rank[i], rank[i+k] if i+k<n else -1))
        tmp[sa[0]] = 0
        for i in range(1, n):
            prev, cur = sa[i-1], sa[i]
            tmp[cur] = tmp[prev] + ((rank[prev], rank[prev+k] if prev+k<n else -1) != (rank[cur], rank[cur+k] if cur+k<n else -1))
        rank, k = tmp[:], k*2
        if rank[sa[-1]] == n-1:
            break
    return sa

def build_lcp(s, sa):
    n = len(s)
    rank = [0]*n
    for i, p in enumerate(sa):
        rank[p] = i
    lcp = [0]*(n-1)
    h = 0
    for i in range(n):
        if rank[i] == n-1:
            h = 0
            continue
        j = sa[rank[i]+1]
        while i+h<n and j+h<n and s[i+h]==s[j+h]:
            h += 1
        lcp[rank[i]] = h
        if h: h -= 1
    return lcp

def lcs_sa(s1, s2):
    sep1, sep2 = chr(1), chr(0)
    S = s1 + sep1 + s2 + sep2
    sa = build_sa(S)
    lcp = build_lcp(S, sa)
    n1 = len(s1)
    maxlen = 0
    for i in range(len(lcp)):
        a, b = sa[i], sa[i+1]
        if (a < n1) != (b < n1):
            maxlen = max(maxlen, lcp[i])
    return maxlen

class SAMNode:
    __slots__ = ('next', 'link', 'len')
    def __init__(self):
        self.next = {}
        self.link = -1
        self.len = 0

class SuffixAutomaton:
    def __init__(self, s):
        self.nodes = [SAMNode()]
        last = 0
        for c in s:
            cur = len(self.nodes)
            self.nodes.append(SAMNode())
            self.nodes[cur].len = self.nodes[last].len + 1
            p = last
            while p >= 0 and c not in self.nodes[p].next:
                self.nodes[p].next[c] = cur
                p = self.nodes[p].link
            if p == -1:
                self.nodes[cur].link = 0
            else:
                q = self.nodes[p].next[c]
                if self.nodes[p].len + 1 == self.nodes[q].len:
                    self.nodes[cur].link = q
                else:
                    clone = len(self.nodes)
                    self.nodes.append(SAMNode())
                    self.nodes[clone].len = self.nodes[p].len + 1
                    self.nodes[clone].next = self.nodes[q].next.copy()
                    self.nodes[clone].link = self.nodes[q].link
                    while p >= 0 and self.nodes[p].next[c] == q:
                        self.nodes[p].next[c] = clone
                        p = self.nodes[p].link
                    self.nodes[q].link = self.nodes[cur].link = clone
            last = cur

    def longest_common_substring(self, t):
        v, l, best = 0, 0, 0
        for c in t:
            while v and c not in self.nodes[v].next:
                v = self.nodes[v].link
                l = self.nodes[v].len
            if c in self.nodes[v].next:
                v = self.nodes[v].next[c]
                l += 1
                best = max(best, l)
            else:
                v, l = 0, 0
        return best

def lcs_sam(s1, s2):
    sam = SuffixAutomaton(s1)
    return sam.longest_common_substring(s2)

# Prepare test cases
test_cases = [
    ("empty", "", ""),
    ("single_diff", "a", "b"),
    ("identical_short", "abcdef", "abcdef"),
    ("no_common", "abcdef", "ghijkl"),
    ("all_same_char", "aaaaaa", "aaaa"),
    ("common_prefix", "prefix_common", "prefix_diff"),
    ("common_suffix", "end_common", "diff_common"),
    ("middle_common", "abcXYZdef", "uvwXYZghi"),
]

# Add random test cases
for i in range(20):
    # 50% random, 50% embed common substring
    if random.random() < 0.5:
        s1 = ''.join(random.choices(string.ascii_lowercase, k=50))
        s2 = ''.join(random.choices(string.ascii_lowercase, k=50))
    else:
        common = ''.join(random.choices(string.ascii_lowercase, k=10))
        s1 = ''.join(random.choices(string.ascii_lowercase, k=20)) + common + ''.join(random.choices(string.ascii_lowercase, k=20))
        s2 = ''.join(random.choices(string.ascii_lowercase, k=15)) + common + ''.join(random.choices(string.ascii_lowercase, k=25))
    test_cases.append((f"random_{i}", s1, s2))

# Run tests
records = []
for name, s1, s2 in test_cases:
    dp = lcs_dp_substr(s1, s2)
    sa = lcs_sa(s1, s2)
    sam = lcs_sam(s1, s2)
    records.append({
        "case": name,
        "lcs_dp": dp,
        "lcs_sa": sa,
        "lcs_sam": sam,
        "all_equal": (dp == sa == sam)
    })

df = pd.DataFrame(records)
# print("Correctness Tests: LCS Methods Comparison", df)
# bez indeksów i z całą zawartością
print(df.to_string(index=False))


import matplotlib.pyplot as plt

# Line plot of LCS lengths per test case
plt.figure(figsize=(10, 4))
plt.plot(df.index, df['lcs_dp'], marker='o', label='DP')
plt.plot(df.index, df['lcs_sa'], marker='s', label='SA')
plt.plot(df.index, df['lcs_sam'], marker='^', label='SAM')
plt.xticks(df.index, df['case'], rotation=90, fontsize=8)
plt.xlabel('Test Case')
plt.ylabel('LCS Length')
plt.title('LCS Lengths Across Test Cases')
plt.legend()
plt.tight_layout()
plt.show()

# Histogram of LCS length distribution
plt.figure(figsize=(6, 4))
plt.hist(df['lcs_dp'], bins='auto')
plt.xlabel('LCS Length')
plt.ylabel('Frequency')
plt.title('Distribution of LCS Lengths')
plt.tight_layout()
plt.show()
