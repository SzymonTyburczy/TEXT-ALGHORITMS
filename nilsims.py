import hashlib
from typing import List, Tuple


class NilsimsHash:
    """Klasa implementująca algorytm Nilsimsa."""

    def __init__(self):
        """Inicjalizuje hash Nilsimsa."""
        self.acc = [0] * 256
        self.total = 0

    def _rolling_hash(self, text: str) -> list[int]:
        """
        Oblicza rolling hash dla tekstu.

        Args:
            text: Tekst do przetworzenia

        Returns:
            Lista wartości rolling hash
        """
        hashes: List[int] = []
        length = len(text)
        for i in range(length):
            c1 = ord(text[i])
            c2 = ord(text[i + 1]) if i + 1 < length else 0
            c3 = ord(text[i + 2]) if i + 2 < length else 0
            bucket = (c1 ^ c2 ^ c3) & 0xFF
            hashes.append(bucket)
        return hashes

    def _trigrams(self, text: str) -> list[str]:
        """
        Generuje trigramy z tekstu.

        Args:
            text: Tekst do przetworzenia

        Returns:
            Lista trigramów
        """
        processed = "".join(ch.lower() for ch in text if ch.isalnum() or ch.isspace())
        length = len(processed)
        if length < 3:
            return []
        return [processed[i: i + 3] for i in range(length - 2)]

    def compute_hash(self, text: str) -> bytes:
        """
        Oblicza hash Nilsimsa dla tekstu.

        Args:
            text: Tekst do zahashowania

        Returns:
            256-bitowy hash jako bytes
        """
        processed = "".join(ch.lower() for ch in text if ch.isalnum() or ch.isspace())
        self.acc = [0] * 256
        self.total = 0
        buckets = self._rolling_hash(processed)
        for b in buckets:
            self.acc[b] += 1
            self.total += 1
        if self.total == 0:
            return bytes(32)
        threshold = self.total / 256.0
        bits = [1 if count > threshold else 0 for count in self.acc]
        digest_bytes = bytearray(32)
        for byte_index in range(32):
            val = 0
            for bit_index in range(8):
                idx = byte_index * 8 + bit_index
                val = (val << 1) | bits[idx]
            digest_bytes[byte_index] = val
        return bytes(digest_bytes)

    def compare_hashes(self, hash1: bytes, hash2: bytes) -> float:
        """
        Porównuje dwa hashe Nilsimsa i zwraca stopień podobieństwa.

        Args:
            hash1: Pierwszy hash
            hash2: Drugi hash

        Returns:
            Stopień podobieństwa w zakresie [0, 1]
        """
        if len(hash1) != 32 or len(hash2) != 32:
            raise ValueError
        total_matches = 0
        for b1, b2 in zip(hash1, hash2):
            diff = b1 ^ b2
            popc = bin(diff).count("1")
            total_matches += (8 - popc)
        return total_matches / 256.0


def nilsims_similarity(text1: str, text2: str) -> float:
    """
    Oblicza podobieństwo między dwoma tekstami używając algorytmu Nilsimsa.

    Args:
        text1: Pierwszy tekst
        text2: Drugi tekst

    Returns:
        Stopień podobieństwa w zakresie [0, 1]
    """
    if not text1 and not text2:
        return 1.0
    if not text1 or not text2:
        return 0.0
    hasher = NilsimsHash()
    h1 = hasher.compute_hash(text1)
    h2 = hasher.compute_hash(text2)
    return hasher.compare_hashes(h1, h2)


def find_similar_texts(target: str, candidates: list[str], threshold: float = 0.7) -> list[tuple[int, float]]:
    """
    Znajduje teksty podobne do tekstu docelowego.

    Args:
        target: Tekst docelowy
        candidates: Lista kandydatów
        threshold: Próg podobieństwa

    Returns:
        Lista krotek (indeks, podobieństwo) dla tekstów powyżej progu
    """
    results = []
    base_hasher = NilsimsHash()
    base_hash = base_hasher.compute_hash(target)
    for idx, candidate in enumerate(candidates):
        h = NilsimsHash().compute_hash(candidate)
        sim = base_hasher.compare_hashes(base_hash, h)
        if sim >= threshold:
            results.append((idx, sim))
    return results



if __name__ == "__main__":
    text1 = "To jest przykładowy tekst do testowania"
    text2 = "To jest przykładowy tekst dla testów"
    sim = nilsims_similarity(text1, text2)
    print(f"{sim:.4f}")

    samples = [
        "To jest przykładowy tekst do testowania",
        "To jest przykładowy tekst dla testów",
        "Całkowicie inny ciąg znaków bez wspólnych słów",
        "To jest PRZYKŁADOWY tekst do Testowania",
        "Przykładowy tekst testowy"
    ]
    for i in range(len(samples)):
        for j in range(i + 1, len(samples)):
            s = nilsims_similarity(samples[i], samples[j])
            print(f"{s:.4f}")

    base = "Przykładowy dokument testowy do porównania"
    corpus = [
        "Przykładowy dokument testowy do porównania",
        "Przykładowy dokument do porownania testowego",
        "Test zupełnie innego tekstu",
        "Przykladowy Dokument Testowy Do Porownania"
    ]
    similar = find_similar_texts(base, corpus, threshold=0.75)
    for idx, score in similar:
        print(f"{idx} -> {score:.4f}")