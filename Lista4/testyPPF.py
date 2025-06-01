from generator import generate_requests
from algorithmsWithDistributionForPPF.fifo import fifo_ppf_procesowy
from algorithmsWithDistributionForPPF.lfu import second_chance_ppf_procesowy
from algorithmsWithDistributionForPPF.lru import lru_ppf_procesowy_z_logiem
from algorithmsWithDistributionForPPF.opt import opt_ppf_procesowy
from algorithmsWithDistributionForPPF.rand import rand_ppf_procesowy
import pandas as pd

# Parametry testu
process_count = 3
total_frames = 150
total_requests = 1000
phases = 2
process_proportions = [0.5, 0.3,0.1]


# Wygeneruj wspólne dane wejściowe
requests, frame_alloc = generate_requests(
    process_count=process_count,
    total_frames=total_frames,
    total_requests=total_requests,
    phases=phases,
    process_proportions=process_proportions
)

# Lista algorytmów do porównania
algorithms = {
    "FIFO": fifo_ppf_procesowy,
    "SecondChance": second_chance_ppf_procesowy,
    "LRU": lru_ppf_procesowy_z_logiem,
    "OPT": opt_ppf_procesowy,
    "RAND": rand_ppf_procesowy
}

# Przechowujemy wyniki
results = []

import matplotlib.pyplot as plt

# Zakres pojemności pamięci wirtualnej do przetestowania
virtual_capacities = list(range(50, 201, 1))

# Przechowujemy wyniki: {algorytm: [lista_błędów_dla_kolejnych_pojemności]}
alg_results = {name: [] for name in algorithms}

# Dla każdego rozmiaru pamięci, uruchom algorytmy i zbierz błędy stron
for vc in virtual_capacities:
    for name, algorithm in algorithms.items():
        bledy, suspended, log = algorithm(
            requests,
            virtual_capacity=vc,
            process_count=process_count,
            process_proportions=process_proportions
        )
        total_faults = sum(bledy.values())
        alg_results[name].append(total_faults)

# Rysujemy wykres
plt.figure(figsize=(12, 6))
for name, faults in alg_results.items():
    plt.plot(virtual_capacities, faults, marker='o', label=name)

plt.title("Liczba błędów stron w zależności od pojemności pamięci wirtualnej")
plt.xlabel("Pojemność pamięci wirtualnej")
plt.ylabel("Liczba błędów stron")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
