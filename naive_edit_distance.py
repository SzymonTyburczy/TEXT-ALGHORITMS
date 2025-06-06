def naive_edit_distance(s1: str, s2: str) -> int:
    """
    Oblicza odległość edycyjną między dwoma ciągami używając naiwnego algorytmu rekurencyjnego.

    Args:
        s1: Pierwszy ciąg znaków
        s2: Drugi ciąg znaków

    Returns:
        Odległość edycyjna (minimalna liczba operacji wstawienia, usunięcia
        lub zamiany znaku potrzebnych do przekształcenia s1 w s2)
    """

    #czasowa 3 do min(m, n)
    #pamiecowa m+n
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)
    if s1[0] == s2[0]:
        return naive_edit_distance(s1[1:], s2[1:])
    insert_cost = 1 + naive_edit_distance(s1, s2[1:])
    delete_cost = 1 + naive_edit_distance(s1[1:], s2)
    replace_cost = 1 + naive_edit_distance(s1[1:], s2[1:])
    return min(insert_cost, delete_cost, replace_cost)


def naive_edit_distance_with_operations(s1: str, s2: str) -> tuple[int, list[str]]:
    """
    Oblicza odległość edycyjną i zwraca listę operacji potrzebnych do przekształcenia s1 w s2.

    Args:
        s1: Pierwszy ciąg znaków
        s2: Drugi ciąg znaków

    Returns:
        Krotka zawierająca odległość edycyjną i listę operacji
        Operacje: "INSERT x", "DELETE x", "REPLACE x->y", "MATCH x"
    """
    if not s1:
        ops = [f"INSERT {c}" for c in s2]
        return (len(s2), ops)
    if not s2:
        ops = [f"DELETE {c}" for c in s1]
        return (len(s1), ops)
    if s1[0] == s2[0]:
        dist_rest, ops_rest = naive_edit_distance_with_operations(s1[1:], s2[1:])
        return (dist_rest, [f"MATCH {s1[0]}"] + ops_rest)
    dist_insert, ops_insert = naive_edit_distance_with_operations(s1, s2[1:])
    dist_insert += 1
    dist_delete, ops_delete = naive_edit_distance_with_operations(s1[1:], s2)
    dist_delete += 1
    dist_replace, ops_replace = naive_edit_distance_with_operations(s1[1:], s2[1:])
    dist_replace += 1
    min_dist = min(dist_insert, dist_delete, dist_replace)
    if min_dist == dist_replace:
        return (dist_replace, [f"REPLACE {s1[0]}->{s2[0]}"] + ops_replace)
    elif min_dist == dist_insert:
        return (dist_insert, [f"INSERT {s2[0]}"] + ops_insert)
    else:
        return (dist_delete, [f"DELETE {s1[0]}"] + ops_delete)

