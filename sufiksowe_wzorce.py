def build_suffix_array(s):
    """
    Construct suffix array for string s in O(n log n) time using doubling algorithm.
    Returns list SA where SA[i] is the starting index of the i-th smallest suffix.
    """
    n = len(s)
    # initial ranking by character
    ranks = [ord(c) for c in s]
    ranks.append(-1)  # sentinel for comparisons
    sa = list(range(n))
    tmp = [0] * n
    k = 1
    while k <= n:
        # sort by (rank[i], rank[i+k]) pairs
        sa.sort(key=lambda i: (ranks[i], ranks[i + k] if i + k < n else -1))
        # temporary ranking
        tmp[sa[0]] = 0
        for i in range(1, n):
            prev, curr = sa[i-1], sa[i]
            prev_pair = (ranks[prev], ranks[prev + k] if prev + k < n else -1)
            curr_pair = (ranks[curr], ranks[curr + k] if curr + k < n else -1)
            tmp[curr] = tmp[prev] + (prev_pair != curr_pair)
        # update ranks
        ranks[:n] = tmp[:]
        k *= 2
        # if all ranks are unique, we are done
        if ranks[sa[-1]] == n - 1:
            break
    return sa


def suffix_array_search(text, pattern):
    """
    Search for all occurrences of pattern in text using suffix array and binary search.
    Returns list of starting indices where pattern occurs.
    """
    sa = build_suffix_array(text)
    n, m = len(text), len(pattern)
    res = []

    # helper to compare pattern with suffix at sa[mid]
    def is_prefix(pos):
        # compare text[pos:pos+m] and pattern
        if pos + m > n:
            return False
        return text[pos:pos+m] == pattern

    # binary search for left bound
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if text[sa[mid]:sa[mid] + m] < pattern:
            lo = mid + 1
        else:
            hi = mid
    left = lo

    # binary search for right bound
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if text[sa[mid]:sa[mid] + m] <= pattern:
            lo = mid + 1
        else:
            hi = mid
    right = lo

    # collect results
    for i in range(left, right):
        res.append(sa[i])
    return sorted(res)

# Example usage:
if __name__ == "__main__":
    text = "banana"
    pattern = "ana"
    positions = suffix_array_search(text, pattern)
    print(f"Pattern '{pattern}' found at positions: {positions}")
