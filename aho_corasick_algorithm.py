from collections import deque, defaultdict

class AhoCorasick:
    def __init__(self, patterns):
        self.goto = []            # lista dictów: goto[state][char] = next_state
        self.fail = []            # lista intów: fail[state] = sufiksowy link
        self.output = []          # lista list: output[state] = wzorce
        self._build_trie(patterns)
        self._build_failure()

    def _new_state(self):
        self.goto.append({})
        self.fail.append(0)
        self.output.append([])
        return len(self.goto) - 1

    def _build_trie(self, patterns):
        self._new_state()  # stan 0 = root
        for pat in patterns:
            state = 0
            for c in pat:
                if c not in self.goto[state]:
                    next_state = self._new_state()
                    self.goto[state][c] = next_state
                state = self.goto[state][c]
            self.output[state].append(pat)

    def _build_failure(self):
        q = deque()
        # inicjalizacja dla dzieci korzenia
        for c, s in self.goto[0].items():
            self.fail[s] = 0
            q.append(s)
        # BFS
        while q:
            r = q.popleft()
            for c, s in self.goto[r].items():
                q.append(s)
                state = self.fail[r]
                # idź sufiksami aż znajdziesz c lub dojdziesz do root
                while state and c not in self.goto[state]:
                    state = self.fail[state]
                self.fail[s] = self.goto[state].get(c, 0)
                # dziedziczymy output
                self.output[s] += self.output[self.fail[s]]

    def search(self, text):
        state = 0
        results = []  # lista par (pozycja, wzorzec)
        for i, c in enumerate(text):
            while state and c not in self.goto[state]:
                state = self.fail[state]
            state = self.goto[state].get(c, 0)
            for pat in self.output[state]:
                results.append((i - len(pat) + 1, pat))
        return results
def search(text, pattern):
    state = AhoCorasick(pattern)
    results = state.search(text)
    return results

# --- Przykład użycia ---
if __name__ == "__main__":
    wzorce = ["he", "she", "his", "hers"]
    ac = AhoCorasick(wzorce)
    tekst = "ahishers"
    for pos, pat in ac.search(tekst):
        print(f"Wzorzec '{pat}' w pozycji {pos} do {pos+len(pat)-1}")
