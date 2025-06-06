def allison_global_alignment(s1: str, s2: str,
                           match_score: int = 2,
                           mismatch_score: int = -1,
                           gap_penalty: int = -1) -> tuple[int, str, str]:
    """
    Znajduje optymalne globalne wyrównanie używając algorytmu Allisona.

    Args:
        s1: Pierwszy ciąg znaków
        s2: Drugi ciąg znaków
        match_score: Punkty za dopasowanie
        mismatch_score: Punkty za niedopasowanie
        gap_penalty: Kara za lukę

    Returns:
        Krotka zawierająca wynik wyrównania i dwa wyrównane ciągi
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        dp[i][0] = dp[i - 1][0] + gap_penalty
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j - 1] + gap_penalty
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            score_diag = dp[i - 1][j - 1] + (match_score if s1[i - 1] == s2[j - 1] else mismatch_score)
            score_up = dp[i - 1][j] + gap_penalty
            score_left = dp[i][j - 1] + gap_penalty
            dp[i][j] = max(score_diag, score_up, score_left)
    aligned_s1 = []
    aligned_s2 = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + (
        match_score if s1[i - 1] == s2[j - 1] else mismatch_score):
            aligned_s1.append(s1[i - 1])
            aligned_s2.append(s2[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + gap_penalty:
            aligned_s1.append(s1[i - 1])
            aligned_s2.append('-')
            i -= 1
        else:
            aligned_s1.append('-')
            aligned_s2.append(s2[j - 1])
            j -= 1
    return dp[m][n], ''.join(reversed(aligned_s1)), ''.join(reversed(aligned_s2))

def allison_local_alignment(s1: str, s2: str,
                          match_score: int = 2,
                          mismatch_score: int = -1,
                          gap_penalty: int = -1) -> tuple[int, str, str, int, int]:
    """
    Znajduje optymalne lokalne wyrównanie (podobnie do algorytmu Smith-Waterman).

    Args:
        s1: Pierwszy ciąg znaków
        s2: Drugi ciąg znaków
        match_score: Punkty za dopasowanie
        mismatch_score: Punkty za niedopasowanie
        gap_penalty: Kara za lukę

    Returns:
        Krotka zawierająca wynik wyrównania, dwa wyrównane ciągi oraz pozycje początku
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_i = max_j = 0
    max_score = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            score_diag = dp[i - 1][j - 1] + (match_score if s1[i - 1] == s2[j - 1] else mismatch_score)
            score_up = dp[i - 1][j] + gap_penalty
            score_left = dp[i][j - 1] + gap_penalty
            dp[i][j] = max(0, score_diag, score_up, score_left)
            if dp[i][j] > max_score:
                max_score = dp[i][j]
                max_i, max_j = i, j
    aligned_s1 = []
    aligned_s2 = []
    i, j = max_i, max_j
    while i > 0 and j > 0 and dp[i][j] > 0:
        if dp[i][j] == dp[i - 1][j - 1] + (match_score if s1[i - 1] == s2[j - 1] else mismatch_score):
            aligned_s1.append(s1[i - 1])
            aligned_s2.append(s2[j - 1])
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i - 1][j] + gap_penalty:
            aligned_s1.append(s1[i - 1])
            aligned_s2.append('-')
            i -= 1
        else:
            aligned_s1.append('-')
            aligned_s2.append(s2[j - 1])
            j -= 1
    aligned_s1 = ''.join(reversed(aligned_s1))
    aligned_s2 = ''.join(reversed(aligned_s2))
    return max_score, aligned_s1, aligned_s2, i, j