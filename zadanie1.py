class Node:
    def __init__(self, start=-1, end=-1):
        self.children = {}  # Słownik przechowujący dzieci: znak -> Node
        self.suffix_link = None  # Łącze sufiksowe (reguła łącza sufiksowego)
        self.start = start  # Indeks początkowy etykiety krawędzi w tekście
        self.end = end  # Indeks końcowy (dla liści to wskaźnik końcowy – może być zmieniany)
        self.suffix_index = -1  # Numer sufiksu (ustawiany przy DFS po zakończeniu budowy drzewa)


class SuffixTree:
    def __init__(self, text: str):
        """
        Budowanie drzewa sufiksów dla zadanego tekstu przy użyciu algorytmu Ukkonena.
        Do tekstu dodawany jest znak '$' kończący.
        """
        self.text = text + "$"
        self.size = len(self.text)
        self.root = Node(-1, -1)
        self.root.suffix_link = self.root
        # Aktywne wskaźniki wykorzystywane przez algorytm
        self.active_node = self.root
        self.active_edge = 0  # indeks w tekście, który oznacza początek aktywnej krawędzi
        self.active_length = 0
        self.remaining = 0  # liczba oczekujących rozszerzeń
        self.last_new_node = None  # ostatni utworzony węzeł wewnętrzny, który oczekuje ustawienia łącza sufiksowego
        self.leaf_end = -1  # globalny wskaźnik końcowy dla wszystkich liści
        self.build_tree()
        self._set_suffix_index(self.root, 0)

    def edge_length(self, node: Node, current_pos: int) -> int:
        """
        Oblicza długość etykiety krawędzi wychodzącej z danego węzła.
        Dla liścia końcowy indeks to aktualna pozycja +1 (technika wskaźnika końcowego).
        """
        return min(node.end, current_pos + 1) - node.start

    def build_tree(self):
        """
        Buduje drzewo sufiksów przy użyciu algorytmu Ukkonena z zastosowaniem:
         - Techniki skip/count
         - Reguły łącza sufiksowego
         - Techniki wskaźnika końcowego
        Złożoność czasowa wynosi O(n) w średnim przypadku.
        """
        for pos in range(self.size):
            self._extend_suffix_tree(pos)

    def _extend_suffix_tree(self, pos: int):
        """
        Rozszerza drzewo sufiksów o znak na pozycji pos.
        """
        self.leaf_end = pos  # aktualizujemy globalny wskaźnik końcowy dla liści
        self.remaining += 1  # nowy sufiks musi zostać dodany
        self.last_new_node = None

        while self.remaining > 0:
            if self.active_length == 0:
                self.active_edge = pos  # nowa aktywna krawędź
            curr_char = self.text[self.active_edge]
            # Jeśli aktualny węzeł nie posiada dziecka zaczynającego się od curr_char, to:
            if curr_char not in self.active_node.children:
                # Utwórz liść (krawędź od pos do końca tekstu)
                leaf = Node(pos, self.size)
                self.active_node.children[curr_char] = leaf

                # Jeśli istniał ostatni węzeł wewnętrzny oczekujący ustawienia łącza, ustaw je na active_node
                if self.last_new_node is not None:
                    self.last_new_node.suffix_link = self.active_node
                    self.last_new_node = None
            else:
                # Aktywna krawędź już istnieje. Pobierz dziecko.
                next_node = self.active_node.children[curr_char]
                edge_len = self.edge_length(next_node, pos)
                # **Technika skip/count:** Jeśli długość aktywnego ciągu jest większa lub równa długości etykiety krawędzi,
                # „przeskocz” całą krawędź.
                if self.active_length >= edge_len:
                    self.active_edge += edge_len
                    self.active_length -= edge_len
                    self.active_node = next_node
                    continue
                # Jeżeli kolejny znak na krawędzi jest taki sam jak znak na pozycji pos,
                # inkrementuj active_length (rozszerzenie jest już zawarte w drzewie)
                if self.text[next_node.start + self.active_length] == self.text[pos]:
                    if self.last_new_node is not None and self.active_node != self.root:
                        self.last_new_node.suffix_link = self.active_node
                        self.last_new_node = None
                    self.active_length += 1
                    break  # następne rozszerzenie rozpoczniemy z następnym znakiem
                # W przeciwnym razie – występuje rozłam (split) krawędzi:
                split_end = next_node.start + self.active_length
                split_node = Node(next_node.start, split_end)
                self.active_node.children[curr_char] = split_node
                # Nowy liść dla bieżącego znaku
                leaf = Node(pos, self.size)
                split_node.children[self.text[pos]] = leaf
                # Aktualizujemy istniejący węzeł: przesuwamy początek krawędzi
                next_node.start += self.active_length
                split_node.children[self.text[next_node.start]] = next_node

                # Ustaw łącze sufiksowe węzła wewnętrznego, jeśli jest to wymagane
                if self.last_new_node is not None:
                    self.last_new_node.suffix_link = split_node
                self.last_new_node = split_node

            self.remaining -= 1

            # Aktualizujemy aktywne wskaźniki
            if self.active_node == self.root and self.active_length > 0:
                self.active_length -= 1
                self.active_edge = pos - self.remaining + 1
            elif self.active_node != self.root:
                self.active_node = self.active_node.suffix_link if self.active_node.suffix_link is not None else self.root

    def _set_suffix_index(self, node: Node, label_length: int):
        """
        Przechodzi przez drzewo sufiksów (DFS) i ustawia końcowy indeks sufiksu dla liści.
        Dzięki temu mamy bezpośrednio zapamiętane pozycje wystąpień sufiksów.
        """
        if len(node.children) == 0:
            node.suffix_index = self.size - label_length
            return
        for child in node.children.values():
            edge_len = (min(child.end, self.size) - child.start)
            self._set_suffix_index(child, label_length + edge_len)

    def find_pattern(self, pattern: str) -> list:
        """
        Wyszukuje wszystkie wystąpienia wzorca w tekście przy pomocy drzewa sufiksów.

        Zasada działania:
         - Przechodzimy drzewo zgodnie z etykietami krawędzi i sprawdzamy czy wzorzec pokrywa się z etykietą.
         - Jeśli uda się dopasować cały wzorzec, zbieramy wszystkie indeksy sufiksów (liść) w poddrzewie.

        Zwraca:
         - Listę pozycji, gdzie wzorzec występuje w tekście.
        """
        current = self.root
        i = 0

        while i < len(pattern):
            char = pattern[i]
            if char not in current.children:
                return []  # wzorzec nie występuje
            child = current.children[char]
            edge_label = self.text[child.start: min(child.end, self.size)]
            j = 0
            # Porównujemy znak po znaku etykietę krawędzi z częścią wzorca
            while j < len(edge_label) and i < len(pattern):
                if pattern[i] != edge_label[j]:
                    return []
                i += 1
                j += 1
            current = child

        # Po dopasowaniu wzorca zbieramy wszystkie indeksy sufiksów z liści w poddrzewie
        result = []
        self._collect_suffix_indices(current, result)
        return sorted(result)

    def _collect_suffix_indices(self, node: Node, result: list):
        """
        Rekurencyjnie zbiera sufiks_indexy z liści (wystąpienia wzorca).
        """
        if node.suffix_index != -1:
            result.append(node.suffix_index)
            return
        for child in node.children.values():
            self._collect_suffix_indices(child, result)


# Przykładowe testy

if __name__ == "__main__":
    def test_case(text, pattern, expected):
        tree = SuffixTree(text)
        result = tree.find_pattern(pattern)
        print(f"Test: '{pattern}' in '{text}'")
        print(f"Expected: {expected}, Got: {result}")
        print("✅ OK\n" if sorted(result) == sorted(expected) else "❌ FAIL\n")

    test_case("banana", "ana", [1, 3])
    test_case("banana", "ban", [0])
    test_case("banana", "nana", [2])
    test_case("banana", "a", [1, 3, 5])
    test_case("banana", "x", [])  # brak dopasowania
    test_case("mississippi", "issi", [1, 4])
    test_case("aaaaa", "aa", [0, 1, 2, 3])  # nakładające się wzorce
    test_case("abcd", "d", [3])
    test_case("abcd", "abcd", [0])
    test_case("abcd", "abcde", [])  # za długi wzorzec
