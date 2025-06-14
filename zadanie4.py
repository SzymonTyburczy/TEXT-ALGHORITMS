"""
benchmark_algorithms.py

Imports various string-search algorithms and compares their build and search times.
"""

import time

from naive_pattern_matching import search_naive
from kmp_algorithm import search_kmp
from boyer_moore_algorithm import search_boyer_moore
from rabin_karp_algorithm import search_rabin_karp
from z_algorithm import search_z
from sufiksowe_wzorce import search_suffix_array
from Ukkonen_algo import search_ukkonen
from aho_corasick_algorithm import search as search_aho

def benchmark(text: str, pattern: str):
    functions = [
        ("Naive", lambda: search_naive(text, pattern)),
        ("KMP", lambda: search_kmp(text, pattern)),
        ("Boyer-Moore", lambda: search_boyer_moore(text, pattern)),
        ("Rabin-Karp", lambda: search_rabin_karp(text, pattern)),
        ("Z-Algorithm", lambda: search_z(text, pattern)),
        ("Suffix Array", lambda: search_suffix_array(text, pattern)),
        ("Ukkonen", lambda: search_ukkonen(text, pattern)),
        ("Aho-Corasick", lambda: search_aho(text, [pattern])),
    ]

    # print(f"{'Algorithm':<20} {'Build (s)':>12} {'Search (s)':>12} {"Memory Usage":>12} {"Porownania":>12} {"Memory per":>12}")
    # print("-" * 80)
    lista = []
    for name, func in functions:
        # run and get metrics
        matches, metrics = func()
        build_time = metrics.get('build_time', 0.0)
        search_time = metrics.get('search_time', 0.0)
        memory_usage = metrics.get('memory_bytes', 0.0)
        comparsions = metrics.get('comparisons', 0.0)
        memory_per = metrics.get('memory_per_char', 0.0)

        lista.append((name, search_time, memory_usage, comparsions, memory_per))
    return lista

def compare():
    lengths = [100, 250, 500, 1000, 2000]
    names = ["Naive", "KMP", "Boyer-Moore", "Rabin-Karp", "Z-Algorithm", "Suffix Array","Ukkonen", "Aho-Corasick"]
    text1= "skibidiohiosigmarizz"
    pattern = "skibidiohiosigm"
    y_val_time = {}
    y_val_memory = {}
    y_val_comps = {}
    y_val_memoryper = {}
    for length in lengths:
        text = text1*length
        wyniki2 = benchmark(text, pattern)
        for wyniki in wyniki2:
            name = wyniki[0]
            search_time = wyniki[1]
            memory_usage = wyniki[2]
            comparsions = wyniki[3]
            memory_per = wyniki[4]


            if name not in y_val_time:
                y_val_time[name] = [search_time]
            else:
                y_val_time[name].append(search_time)

            if name not in y_val_memory:
                y_val_memory[name] = [memory_usage]
            else:
                y_val_memory[name].append(memory_usage)

            if name not in y_val_comps:
                y_val_comps[name] = [comparsions]
            else:
                y_val_comps[name].append(comparsions)

            if name not in y_val_memoryper:
                y_val_memoryper[name] = []
            else:
                y_val_memoryper[name].append(memory_per)

    def scale_list(lst, factor):
        """
        Zwraca nową listę, w której każdy element lst
        został pomnożony przez factor.
        """
        return [x * factor for x in lst]
    lengths = scale_list(lengths, len(text1))
    return names, lengths, y_val_time, y_val_memory, y_val_comps, y_val_memoryper
k = compare()
# names, x_vals, y_val_time, y_val_memory, y_val_comps, y_val_memoryper = compare()

x_vals = k[1]
names = k[0]
import matplotlib.pyplot as plt
#czasy
plt.figure(figsize=(8,5))

for name in names:
    plt.plot(x_vals, k[2][name], marker='o', label=name)

plt.title('Porównanie algorytmów')
plt.xlabel('Długość tekstu')
plt.ylabel('Czas wykonania w MS')
plt.legend()                   # wyświetla legendę, która kojarzy kolor z nazwą
plt.grid(True)                 # (opcjonalnie) siatka ułatwiająca odczyt
plt.tight_layout()
plt.show()


#memordy
plt.figure(figsize=(8,5))
for name in names:
    plt.plot(x_vals, k[3][name], marker='o', label=name)

plt.title('Porównanie algorytmów')
plt.xlabel('Długość tekstu')
plt.ylabel('Użycie pamięci w bajtach')
plt.legend()                   # wyświetla legendę, która kojarzy kolor z nazwą
plt.grid(True)                 # (opcjonalnie) siatka ułatwiająca odczyt
plt.yscale('log')
plt.tight_layout()
plt.show()

#porownaia
plt.figure(figsize=(8,5))
for name in names:
    plt.plot(x_vals, k[4][name], marker='o', label=name)

plt.title('Porównanie algorytmów')
plt.xlabel('Długość tekstu')
plt.ylabel('Liczba porównań')
plt.legend()                   # wyświetla legendę, która kojarzy kolor z nazwą
plt.grid(True)                 # (opcjonalnie) siatka ułatwiająca odczyt
plt.tight_layout()
plt.show()


#czas od wzorca
def compare2():
    lengths = [1, 2, 5, 10, 20]
    names = ["Naive", "KMP", "Boyer-Moore", "Rabin-Karp", "Z-Algorithm", "Suffix Array","Ukkonen", "Aho-Corasick"]
    text1= "sa"*1000
    y_val_time = {}
    y_val_memory = {}
    y_val_comps = {}
    y_val_memoryper = {}
    for length in lengths:
        pattern = "sa"*length
        wyniki2 = benchmark(text1, pattern)
        for wyniki in wyniki2:
            name = wyniki[0]
            search_time = wyniki[1]
            if name not in y_val_time:
                y_val_time[name] = [search_time]
            else:
                y_val_time[name].append(search_time)

    def scale_list(lst, factor):
        """
        Zwraca nową listę, w której każdy element lst
        został pomnożony przez factor.
        """
        return [x * factor for x in lst]
    lengths = scale_list(lengths, 2)
    return names, lengths, y_val_time
p = compare2()
x_vals_wzorzec = p[1]
plt.figure(figsize=(8,5))
for name in names:
    plt.plot(x_vals_wzorzec, p[2][name], marker='o', label=name)

plt.title('Porównanie algorytmów')
plt.xlabel('Długość wzorca')
plt.ylabel('Czas wykonania w MS')
plt.legend()                   # wyświetla legendę, która kojarzy kolor z nazwą
plt.grid(True)                 # (opcjonalnie) siatka ułatwiająca odczyt
plt.tight_layout()
plt.show()











def compare3():
    lengths = [2, 5, 10, 20, 30]
    names = ["Naive", "KMP", "Boyer-Moore", "Rabin-Karp", "Z-Algorithm", "Suffix Array","Ukkonen", "Aho-Corasick"]
    text1= "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce vulputate justo tellus, sit amet vehicula magna fringilla eu. Integer a pulvinar dui. Maecenas justo mauris, convallis ac massa et, sollicitudin lobortis ipsum. Cras eleifend vel elit id mollis. Maecenas sollicitudin dui lorem, sed condimentum orci blandit ut. Integer lacinia magna eget metus imperdiet elementum. Nulla vel neque diam. Aenean ac nulla eleifend, vestibulum ligula nec, iaculis ex. Aliquam ut metus neque. Aliquam laoreet ornare tellus sed scelerisque.eque tellus, vitae imperdiet lectus sagittis id. Integer cursus viverra tellus, vel placerat lacus laoreet vel. Nam vestibulum molestie lectus et fringilla. Suspendisse varius elit non congue posuere. Sed fermentum magna non risus tempor consectetur. Nunc ipsum metus, faucibus nec elit nec, ultricies faucibus dolor. Morbi vel vestibulum massa. Nunc iaculis sit amet erat id rhoncus. Nullam mi quam, viverra ac est nec, fringilla ultrices lectus. Duis nunc nibh, facilisis vel blandit et, accumsan sit amet lectus."
    pattern = "a"
    y_val_time = {}
    y_val_memory = {}
    y_val_comps = {}
    y_val_memoryper = {}
    for length in lengths:
        text = text1*length
        wyniki2 = benchmark(text, pattern)
        for wyniki in wyniki2:
            name = wyniki[0]
            search_time = wyniki[1]
            memory_usage = wyniki[2]
            comparsions = wyniki[3]
            memory_per = wyniki[4]


            if name not in y_val_time:
                y_val_time[name] = [search_time]
            else:
                y_val_time[name].append(search_time)

            if name not in y_val_memory:
                y_val_memory[name] = [memory_usage]
            else:
                y_val_memory[name].append(memory_usage)

            if name not in y_val_comps:
                y_val_comps[name] = [comparsions]
            else:
                y_val_comps[name].append(comparsions)

            if name not in y_val_memoryper:
                y_val_memoryper[name] = []
            else:
                y_val_memoryper[name].append(memory_per)

    def scale_list(lst, factor):
        """
        Zwraca nową listę, w której każdy element lst
        został pomnożony przez factor.
        """
        return [x * factor for x in lst]
    lengths = scale_list(lengths, len(text1))
    return names, lengths, y_val_time, y_val_memory, y_val_comps, y_val_memoryper
f = compare3()
# names, x_vals, y_val_time, y_val_memory, y_val_comps, y_val_memoryper = compare()

x_vals = f[1]
names = f[0]
import matplotlib.pyplot as plt
#czasy
plt.figure(figsize=(8,5))

for name in names:
    plt.plot(x_vals, f[2][name], marker='o', label=name)

plt.title('Porównanie algorytmów')
plt.xlabel('Długość tekstu')
plt.ylabel('Czas wykonania w MS')
plt.legend()                   # wyświetla legendę, która kojarzy kolor z nazwą
plt.grid(True)                 # (opcjonalnie) siatka ułatwiająca odczyt
plt.tight_layout()
plt.show()


