class Node:
    def __init__(self):
        self.children = {}        # mapa: znak → Node (wszystkie wychodzące krawędzie)
        self.suffix_link = None   # wskaźnik sufiksowy (Reguła 3)
        self.start = -1           # początek etykiety krawędzi (indeks w self.text)
        self.end = -1             # koniec etykiety krawędzi (indeks w self.text)
        self.id = -1              # (opcjonalne) unikalny identyfikator węzła do debugowania
        self.suffix_index = -1    # dla liści: pozycja sufiksu w oryginalnym tekście; dla węzłów wewnętrznych: -1

    def edge_length(self, current_end):
        """
        Zwraca długość etykiety krawędzi prowadzącej do tego węzła.
        Jeśli to węzeł-liść, używamy współdzielonego `current_end` (leaf_end).
        """
        return min(self.end, current_end) - self.start + 1


class SuffixTree:
    def __init__(self, text: str):
        """
        Buduje drzewo sufiksów dla danego tekstu za pomocą algorytmu Ukkonena.
        """
        # 1) Doklejamy sentinel '$', który jest mniejszy od wszystkich innych znaków
        self.text = text + "$"
        self.size = len(self.text)

        # 2) Inicjalizacja struktury Ukkonena
        self.root = Node()
        self.root.suffix_link = self.root  # suffix_link korzenia → korzeń
        self.active_node = self.root
        self.active_edge = 0
        self.active_length = 0
        self.remainder = 0

        # 3) Wspólny wskaźnik końca etykiet liści
        self.leaf_end = -1

        # 4) Pomocniczy licznik unikalnych identyfikatorów węzłów (opcjonalnie)
        self._last_node_id = 0

        # 5) Budujemy drzewo
        self.build_tree()

    def _new_node(self, start, end, suffix_start=-1):
        """
        Tworzy i zwraca nowy węzeł z etykietą [start..end] w self.text.
        Jeżeli `suffix_start != -1`, to jest to węzeł-liść i wtedy
        ustawiamy node.suffix_index = suffix_start.
        Węzeł wewnętrzny (suffix_start = -1) ma suffix_index = -1.
        """
        node = Node()
        node.start = start
        node.end = end
        node.id = self._last_node_id
        self._last_node_id += 1

        # Domyślny suffix_link do root
        node.suffix_link = self.root

        # Jeśli to węzeł-liść, zapamiętujemy prawdziwą pozycję początku sufiksu
        node.suffix_index = suffix_start
        return node

    def build_tree(self):
        """
        Implementacja algorytmu Ukkonena do budowy drzewa sufiksów w czasie O(n).
        """
        self.root.suffix_link = self.root
        self.active_node = self.root
        self.active_edge = 0
        self.active_length = 0
        self.remainder = 0
        self.leaf_end = -1
        self._last_node_id = 0

        for pos in range(self.size):
            # Rozpoczynamy nową fazę dla pozycji `pos`
            self.leaf_end = pos
            self.remainder += 1
            self.last_new_node = None

            # Dopóki są nierozwiązane sufiksy (remainder > 0), wprowadzamy je do drzewa
            while self.remainder > 0:
                if self.active_length == 0:
                    # Jeśli active_length = 0, to active_edge = bieżący indeks pos
                    self.active_edge = pos

                edge_char = self.text[self.active_edge]
                # 1) Jeżeli nie ma krawędzi z active_node zaczynającej się od edge_char → tworzymy liść
                if edge_char not in self.active_node.children:
                    # Tworzymy nowy węzeł-liść: [pos .. leaf_end], suffix_index = pos
                    leaf = self._new_node(pos, self.size - 1, suffix_start=pos)
                    self.active_node.children[edge_char] = leaf

                    # Jeżeli utworzono wcześniej jakiś węzeł wewnętrzny w tej fazie,
                    # ustawiamy jego suffix_link → active_node
                    if self.last_new_node is not None:
                        self.last_new_node.suffix_link = self.active_node
                        self.last_new_node = None

                    # Zużywamy jeden sufiks
                    self.remainder -= 1
                else:
                    # 2) Krawędź istnieje → przechodzimy skip/count
                    next_node = self.active_node.children[edge_char]
                    edge_len = next_node.edge_length(self.leaf_end)

                    # Jeżeli active_length >= długość etykiety krawędzi → schodzimy niżej
                    if self.active_length >= edge_len:
                        self.active_edge += edge_len
                        self.active_length -= edge_len
                        self.active_node = next_node
                        continue

                    # Jesteśmy w połowie krawędzi → porównujemy kolejny znak
                    if self.text[next_node.start + self.active_length] == self.text[pos]:
                        # Reguła 3: sufiks już jest w drzewie, tylko rozszerzamy active_length
                        self.active_length += 1

                        # Jeśli był utworzony jakiś węzeł wewnętrzny, ustawiamy jego suffix_link
                        if self.last_new_node is not None:
                            self.last_new_node.suffix_link = self.active_node
                            self.last_new_node = None

                        # Nie zmniejszamy remainder, opuszczamy pętlę "while"
                        break

                    # 3) Rozszczepiamy krawędź (split)
                    split_end = next_node.start + self.active_length - 1
                    split_node = self._new_node(next_node.start, split_end)
                    self.active_node.children[edge_char] = split_node

                    # Przechodzimy "stare" dziecko jako dziecko split_node, zaktualizowanym startem
                    next_node.start += self.active_length
                    split_node.children[self.text[next_node.start]] = next_node

                    # Tworzymy nowy liść dla aktualnego sufiksu pos
                    leaf = self._new_node(pos, self.size - 1, suffix_start=pos)
                    split_node.children[self.text[pos]] = leaf

                    # Jeżeli był utworzony jakiś węzeł wewnętrzny w bieżącej fazie,
                    # ustawiamy jego suffix_link → split_node
                    if self.last_new_node is not None:
                        self.last_new_node.suffix_link = split_node

                    # Teraz split_node jest „last_new_node”
                    self.last_new_node = split_node

                    # Domyślny suffix_link split_node → root
                    split_node.suffix_link = self.root

                    # Zużywamy jeden sufiks
                    self.remainder -= 1

                # 4) Aktualizacja aktywnego punktu (active_point)
                if self.active_node == self.root and self.active_length > 0:
                    # Jeżeli w korzeniu i active_length > 0, to skracamy from left
                    self.active_length -= 1
                    self.active_edge = pos - self.remainder + 1
                elif self.active_node != self.root:
                    # Jeżeli nie jesteśmy w korzeniu, zjeżdżamy suffix_link
                    self.active_node = self.active_node.suffix_link
                # W przeciwnym razie, jeżeli jesteśmy w korzeniu i active_length = 0, nie robimy nic więcej

    def _collect_leaf_positions(self, node, result):
        """
        Rekurencyjnie zbiera pole `suffix_index` ze wszystkich węzłów-liści
        w poddrzewie wyrastającym z `node`. Dodaje je do listy result.
        """
        if not node.children:
            # To jest liść → dodajemy suffix_index (pozycję sufiksu w oryginalnym tekście)
            result.append(node.suffix_index)
            return

        for child in node.children.values():
            self._collect_leaf_positions(child, result)

    def find_pattern(self, pattern: str) -> list[int]:
        """
        Znajduje wszystkie wystąpienia `pattern` w oryginalnym tekście
        (bez sentinela '$'). Zwraca posortowaną listę pozycji (0-indeksowanych).
        Jeśli wzorzec nie występuje, zwraca pustą listę.
        """
        node = self.root
        idx = 0  # indeks w `pattern`

        while idx < len(pattern):
            c = pattern[idx]
            # Jeżeli nie ma krawędzi zaczynającej się od c → wzorzec nie istnieje
            if c not in node.children:
                return []

            next_node = node.children[c]
            edge_len = next_node.edge_length(self.leaf_end)
            # Etykieta tej krawędzi:
            label = self.text[next_node.start : next_node.start + edge_len]

            # Ile znaków ze wzorca możemy sprawdzić na tej krawędzi?
            length_to_check = min(len(label), len(pattern) - idx)
            # Jeśli ciąg się nie zgadza → brak dopasowania
            if pattern[idx : idx + length_to_check] != label[:length_to_check]:
                return []

            idx += length_to_check
            if length_to_check < edge_len:
                # Wzorzec kończy się w połowie krawędzi → zbieramy wszystkie liście z next_node
                result = []
                self._collect_leaf_positions(next_node, result)
                return sorted(result)

            # W całości przeszliśmy przez etykietę → schodzimy do węzła
            node = next_node

        # Wzorzec dopasowuje się dokładnie do jakiegoś węzła → zbieramy liście
        result = []
        self._collect_leaf_positions(node, result)
        return sorted(result)


# =========================== TESTY ===========================
if __name__ == "__main__":
    # 1) Przykład: "banana"
    text = "banana"
    st = SuffixTree(text)

    print("=== Tekst: 'banana' ===")
    for pat in ["ana", "nan", "ba", "nana", "x"]:
        wynik = st.find_pattern(pat)
        print(f"Wzorzec '{pat}' → pozycje: {wynik}")
    # Oczekiwane:
    #   'ana'  → [1, 3]
    #   'nan'  → [2]
    #   'ba'   → [0]
    #   'nana' → [2]
    #   'x'    → []

    # 2) Przykład: "abracadabra"
    text2 = "abracadabra"
    st2 = SuffixTree(text2)
    print("\n=== Tekst: 'abracadabra' ===")
    for pat in ["abra", "cad", "ra", "a"]:
        wynik = st2.find_pattern(pat)
        print(f"Wzorzec '{pat}' → pozycje: {wynik}")
    # Oczekiwane:
    #   'abra' → [0, 7]
    #   'cad'  → [4]
    #   'ra'   → [2, 9]
    #   'a'    → [0, 3, 5, 7, 10]

    # 3) Przykład: unikalny tekst "abcdef"
    text3 = "abcdef"
    st3 = SuffixTree(text3)
    print("\n=== Tekst: 'abcdef' ===")
    for pat in ["a", "z", "f", "ef", "bc", "abcdef"]:
        wynik = st3.find_pattern(pat)
        print(f"Wzorzec '{pat}' → pozycje: {wynik}")
    # Oczekiwane:
    #   'a'      → [0]
    #   'z'      → []
    #   'f'      → [5]
    #   'ef'     → [4]
    #   'bc'     → [1]
    #   'abcdef' → [0]
