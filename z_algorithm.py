def compute_z_array(s: str) -> list[int]:
    """
    Compute the Z array for a string.

    The Z array Z[i] gives the length of the longest substring starting at position i
    that is also a prefix of the string.

    Args:
        s: The input string

    Returns:
        The Z array for the string
    """
    # TODO: Implement the Z-array computation
    # For each position i:
    # - Calculate the length of the longest substring starting at i that is also a prefix of s
    # - Use the Z-box technique to avoid redundant character comparisons
    # - Handle the cases when i is inside or outside the current Z-box

    n = len(s)
    Z = [0] * n
    left, right = 0, 0
    for i in range(1, n):
        if i > right:
            left = right = i
            while right < n and s[right - left] == s[right]:
                right += 1
            Z[i] = right - left
            right -= 1
        else:
            k = i - left
            if Z[k] < right - i + 1:
                Z[i] = Z[k]
            else:
                left = i
                while right < n and s[right - left] == s[right]:
                    right += 1
                Z[i] = right - left
                right -= 1
    return Z


def z_pattern_match(text: str, pattern: str) -> list[int]:
    """
    Use the Z algorithm to find all occurrences of a pattern in a text.

    Args:
        text: The text to search in
        pattern: The pattern to search for

    Returns:
        A list of starting positions (0-indexed) where the pattern was found in the text
    """
    # TODO: Implement pattern matching using the Z algorithm
    # 1. Create a concatenated string: pattern + special_character + text
    # 2. Compute the Z array for this concatenated string
    # 3. Find positions where Z[i] equals the pattern length
    # 4. Convert these positions in the concatenated string to positions in the original text
    # 5. Return all positions where the pattern is found in the text

    if not pattern:
        return []
    concatenated = pattern + "$" + text
    Z = compute_z_array(concatenated)
    positions = []
    m = len(pattern)
    for i in range(len(Z)):
        if Z[i] == m:
            positions.append(i - m - 1)
    return positions