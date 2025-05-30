def rabin_karp_pattern_match(text: str, pattern: str, prime: int = 101) -> list[int]:
    """
    Implementation of the Rabin-Karp pattern matching algorithm.

    Args:
        text: The text to search in
        pattern: The pattern to search for
        prime: A prime number used for the hash function

    Returns:
        A list of starting positions (0-indexed) where the pattern was found in the text
    """
    # TODO: Implement the Rabin-Karp string matching algorithm
    # This algorithm uses hashing to find pattern matches:
    # 1. Compute the hash value of the pattern
    # 2. Compute the hash value of each text window of length equal to pattern length
    # 3. If the hash values match, verify character by character to avoid hash collisions
    # 4. Use rolling hash to efficiently compute hash values of text windows
    # 5. Return all positions where the pattern is found in the text
    # Note: Use the provided prime parameter for the hash function to avoid collisions
    n = len(text)
    m = len(pattern)
    if m == 0 or n < m:
        return []
    result = []
    d = 256
    q = 101
    h = 1
    for i in range(m - 1):
        h = (h * d) % q
    p = 0
    t = 0
    for i in range(m):
        p = (p * d + ord(pattern[i])) % q
        t = (t * d + ord(text[i])) % q
    for i in range(n - m + 1):
        if p == t and text[i:i + m] == pattern:
            result.append(i)
        if i < n - m:
            t = (d * (t - ord(text[i]) * h) + ord(text[i + m])) % q
            if t < 0:
                t += q
    return result