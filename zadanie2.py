class Node:
    def __init__(self):
        self.children = {}

class Edge:
    def __init__(self, start, end, dest):
        self.start = start
        self.end = end
        self.dest = dest


def build_suffix_tree(s: str) -> Node:
    """
    Build a (naive) suffix tree for string s using edge-label compression.
    Time complexity: O(n^2), space O(n^2), for demonstration.
    """
    root = Node()
    n = len(s)
    for i in range(n):
        node = root
        j = i
        while j < n:
            c = s[j]
            if c not in node.children:
                leaf = Node()
                node.children[c] = Edge(j, n, leaf)
                break
            edge = node.children[c]
            label_len = edge.end - edge.start
            k = 0
            while k < label_len and j + k < n and s[edge.start + k] == s[j + k]:
                k += 1
            if k == label_len:
                node = edge.dest
                j += k
            else:
                mid = Node()
                node.children[c] = Edge(edge.start, edge.start + k, mid)
                mid.children[s[edge.start + k]] = Edge(edge.start + k, edge.end, edge.dest)
                leaf = Node()
                mid.children[s[j + k]] = Edge(j + k, n, leaf)
                break
    return root


def longest_common_substring(str1: str, str2: str) -> str:
    sep1 = '#'
    sep2 = '$'
    assert sep1 not in str1 and sep1 not in str2
    assert sep2 not in str1 and sep2 not in str2
    s = str1 + sep1 + str2 + sep2

    root = build_suffix_tree(s)
    n1 = len(str1)
    n = len(s)
    best = ""
    def dfs(node: Node, depth: int, path: list) -> (bool, bool):
        nonlocal best
        has1 = False
        has2 = False
        if not node.children:
            start_idx = n - depth
            if start_idx < n1:
                has1 = True
            elif n1 < start_idx < n - 1:
                has2 = True
            return has1, has2
        for edge in node.children.values():
            edge_label = s[edge.start:edge.end]
            path.append(edge_label)
            c1, c2 = dfs(edge.dest, depth + len(edge_label), path)
            path.pop()
            if c1 and c2:
                substr = ''.join(path) + edge_label
                if len(substr) > len(best):
                    best = substr
            has1 |= c1
            has2 |= c2
        return has1, has2

    dfs(root, 0, [])
    return best




def longest_common_substring_multiple(strings: list[str]) -> str:
    if not strings:
        return ""
    k = len(strings)
    separators = [chr(i + 1) for i in range(k)]
    for sep, s in zip(separators, strings):
        if sep in s:
            raise ValueError("Input strings contain control characters used as separators")
    concat = []
    owner = []
    for idx, s in enumerate(strings):
        concat.extend(s)
        owner.extend([idx] * len(s))
        concat.append(separators[idx])
        owner.append(-1)  # separator
    S = "".join(concat)
    n = len(S)
    def build_sa(s: str) -> list[int]:
        n = len(s)
        k = 1
        rank = [ord(c) for c in s]
        tmp = [0] * n
        sa = list(range(n))
        while True:
            sa.sort(key=lambda i: (rank[i], rank[i + k] if i + k < n else -1))
            tmp[sa[0]] = 0
            for i in range(1, n):
                prev, curr = sa[i - 1], sa[i]
                prev_key = (rank[prev], rank[prev + k] if prev + k < n else -1)
                curr_key = (rank[curr], rank[curr + k] if curr + k < n else -1)
                tmp[curr] = tmp[prev] + (prev_key < curr_key)
            rank, tmp = tmp, rank
            if rank[sa[-1]] == n - 1:
                break
            k <<= 1
        return sa
    def build_lcp(s: str, sa: list[int]) -> list[int]:
        n = len(s)
        rank = [0] * n
        for i, pos in enumerate(sa):
            rank[pos] = i
        lcp = [0] * (n - 1)
        h = 0
        for i in range(n):
            if rank[i] > 0:
                j = sa[rank[i] - 1]
                while i + h < n and j + h < n and s[i + h] == s[j + h]:
                    h += 1
                lcp[rank[i] - 1] = h
                if h:
                    h -= 1
        return lcp

    sa = build_sa(S)
    lcp = build_lcp(S, sa)
    from collections import Counter

    count = Counter()
    distinct = 0
    best_len = 0
    best_substr = ""
    left = 0
    for right in range(n):
        o = owner[sa[right]]
        if o >= 0:
            count[o] += 1
            if count[o] == 1:
                distinct += 1
        while distinct == k and left <= right:
            if right - left + 1 >= k:
                # Compute minimal LCP in this window
                window_lcp = lcp[left:right]  # lcp between sa[left..right]
                curr_len = min(window_lcp) if window_lcp else 0
                if curr_len > best_len:
                    best_len = curr_len
                    # Find position of minimal LCP
                    idx_min = window_lcp.index(curr_len)
                    pos = sa[left + idx_min]
                    best_substr = S[pos: pos + curr_len]
            # Remove left element
            o_left = owner[sa[left]]
            if o_left >= 0:
                count[o_left] -= 1
                if count[o_left] == 0:
                    distinct -= 1
            left += 1

    return best_substr

result = longest_common_substring_multiple(["kot", "kotpies", "oko"])
print(result)



def longest_palindromic_substring(text: str) -> str:
    if not text:
        return ""

    t = '#' + '#'.join(text) + '#'
    n = len(t)
    P = [0] * n
    C = R = 0

    for i in range(n):
        mirror = 2*C - i
        if i < R:
            P[i] = min(R - i, P[mirror])
        a = i + P[i] + 1
        b = i - P[i] - 1
        while a < n and b >= 0 and t[a] == t[b]:
            P[i] += 1
            a += 1
            b -= 1
        if i + P[i] > R:
            C = i
            R = i + P[i]
    max_len = max(P)
    center_index = P.index(max_len)
    start = (center_index - max_len) // 2
    return text[start:start + max_len]


if __name__ == "__main__":
    def testcase1():
        assert longest_common_substring("abcdef", "abcdef") == "abcdef"
        assert longest_common_substring("abc", "def") == ""
        assert longest_common_substring("abc", "zcay") == "a"
        assert longest_common_substring("abcdef", "abcxyz") == "abc"
        assert longest_common_substring("xyzabc", "defabc") == "abc"
        assert longest_common_substring("xyabcde", "zzabczz") == "abc"
        assert longest_common_substring("aaaa", "aa") == "aa"
        assert longest_common_substring("", "") == ""
        assert longest_common_substring("abc", "") == ""
        assert longest_common_substring("", "abc") == ""
        assert longest_common_substring("abXYab", "abZZab") == "ab"
        assert longest_common_substring("ababab", "babab") == "babab"
        assert longest_common_substring("hello world", "hello") == "hello"

        print("TESTY 1: All tests passed.")

    def testcase2():
        assert longest_common_substring_multiple(["kot", "kotpies", "oko"]) == "ko"
        assert longest_common_substring_multiple(["kot", "kfadss", "oko"]) == "k"
        assert longest_common_substring_multiple(["flower", "flow", "flight"]) == "fl"
        assert longest_common_substring_multiple(["dog", "racecar", "car"]) == ""
        assert longest_common_substring_multiple([]) == ""
        assert longest_common_substring_multiple(["ppp", "ppppppp", "pppppp"]) == "ppp"
        print("TESTY 2: All tests passed.")
    def testcase3():
        cases = [
            "",
            "a",
            "ab",
            "bb",
            "babad",
            "cbbd",
            "forgeeksskeegfor",
            "abacdfgdcaba",
            "abacdgfdcaba",
        ]
        for s in cases:
            print(f"Input: {s}\nLongest Palindromic Substring: {longest_palindromic_substring(s)}\n")
        print("All tests passed.")



    testcase1()
    testcase2()
    testcase3()



def longest_common_substring_dp(str1, str2):
    # Dynamic programming approach, O(n*m)
    n, m = len(str1), len(str2)
    dp = [0] * (m + 1)
    best = ""
    best_len = 0
    for i in range(n):
        for j in range(m, 0, -1):
            if str1[i] == str2[j-1]:
                dp[j] = dp[j-1] + 1
                if dp[j] > best_len:
                    best_len = dp[j]
                    best = str1[i-best_len+1:i+1]
            else:
                dp[j] = 0
    return best



import random
import string
import time
import matplotlib.pyplot as plt
lengths = [50, 100, 200, 400]
times_tree, times_sa, times_dp = [], [], []
repeats = 3

random.seed(0)
for n in lengths:
    total_tree = total_sa = total_dp = 0
    for _ in range(repeats):
        s1 = ''.join(random.choices(string.ascii_lowercase, k=n))
        s2 = ''.join(random.choices(string.ascii_lowercase, k=n))
        start = time.perf_counter(); longest_common_substring(s1, s2); total_tree += time.perf_counter() - start
        start = time.perf_counter(); longest_common_substring_dp(s1, s2); total_dp += time.perf_counter() - start
    times_tree.append(total_tree / repeats)
    times_sa.append(total_sa / repeats)
    times_dp.append(total_dp / repeats)

# Plot results
plt.figure()
plt.plot(lengths, times_tree, marker='o', label='Suffix Tree')
plt.plot(lengths, times_dp, marker='o', label='Dynamic Programming')
plt.xlabel('Długość ciągów')
plt.ylabel('Czas wykonania (s)')
plt.title('Porównanie wydajności algorytmów LCS (substring)')
plt.legend()
plt.show()

def longest_palindromic_subsequence(s: str) -> str:
    """
    Zwraca najdłuższą palindromiczną podciąg (subsequence) w s.
    Dynamic programming:
      dp[i][j] = długość LPS w s[i..j]
    Rekonstrukcja: idziemy od krańców w górę po tabeli dp.
    """
    n = len(s)
    if n == 0:
        return ""
    # dp[i][j] = długość LPS w s[i..j]
    dp = [[0] * n for _ in range(n)]
    # Każdy pojedynczy znak to palindrom o długości 1
    for i in range(n):
        dp[i][i] = 1

    # Rozważamy podciągi coraz dłuższe: len_sub od 2 do n
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                # Zewnętrzne znaki się zgadzają
                dp[i][j] = 2 + (dp[i + 1][j - 1] if i + 1 <= j - 1 else 0)
            else:
                # Bierzemy maksymalny z pominięcia lewego lub prawego
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])

    # Rekonstrukcja rozwiązania:
    i, j = 0, n - 1
    left_part, right_part = [], []
    while i <= j:
        if s[i] == s[j]:
            # Ten znak bierze udział w LPS
            left_part.append(s[i])
            if i != j:
                right_part.append(s[j])
            i += 1
            j -= 1
        else:
            # Idziemy w kierunku większej wartości dp
            if dp[i + 1][j] >= dp[i][j - 1]:
                i += 1
            else:
                j -= 1

    # scalamy połowy (środek może być pojedynczym znakiem)
    return "".join(left_part) + "".join(reversed(right_part))

lengths = [50, 100, 200, 400]
times_tree, times_sa, times_dp = [], [], []
repeats = 3

random.seed(0)
for n in lengths:
    total_tree = total_sa = total_dp = 0
    for _ in range(repeats):
        s1 = ''.join(random.choices(string.ascii_lowercase, k=n))
        s2 = ''.join(random.choices(string.ascii_lowercase, k=n))
        start = time.perf_counter(); longest_palindromic_substring(s1); total_tree += time.perf_counter() - start
        start = time.perf_counter(); longest_palindromic_subsequence(s1); total_dp += time.perf_counter() - start
    times_tree.append(total_tree / repeats)
    times_sa.append(total_sa / repeats)
    times_dp.append(total_dp / repeats)

# Plot results
plt.figure()
plt.plot(lengths, times_tree, marker='o', label='Palindrome Suffix')
plt.plot(lengths, times_dp, marker='o', label='Palindrome Dynamic Programming')
plt.xlabel('Długość ciągów')
plt.ylabel('Czas wykonania (s)')
plt.title('Porównanie wydajności algorytmów LCS (substring)')
plt.legend()
plt.show()