from generator import generate_requests
from algorithmsWithDistrubution.fifo import fifo_procesowy
from algorithmsWithDistrubution.lfu import second_chance_procesowy
from algorithmsWithDistrubution.lru import lru_procesowy
from algorithmsWithDistrubution.opt import opt_procesowy
from algorithmsWithDistrubution.rand import rand_procesowy
import matplotlib.pyplot as plt
import copy

# Parametry testu
#-----------------------------------------------------------------------------------------------
process_count = 4
total_frames = 150
total_requests = 1000
phases = 2
process_proportions = [0.5,0.2,0.2,0.1]
#-----------------------------------------------------------------------------------------------

# Generowanie wspólnego zestawu danych
#-----------------------------------------------------------------------------------------------
requests, frame_alloc = generate_requests(
    process_count=process_count,
    total_frames=total_frames,
    total_requests=total_requests,
    phases=phases,
    process_proportions=process_proportions
)
#-----------------------------------------------------------------------------------------------

# Zakres pamięci fizycznej
#-----------------------------------------------------------------------------------------------
physical_capacities = range(50, 1001, 10)
#-----------------------------------------------------------------------------------------------

# Sumaryczne wyniki
#-----------------------------------------------------------------------------------------------
results = {
    'FIFO': [],
    'SC': [],
    'LRU': [],
    'OPT': [],
    'RAND': []
}
#-----------------------------------------------------------------------------------------------

# WYNIKI W ZALEŻNOŚCI OD PROCESU DLA KAŻDEGO ALGORYTMU
#-----------------------------------------------------------------------------------------------
results_per_process = {
    'FIFO': {pid: [] for pid in range(process_count)},
    'SC': {pid: [] for pid in range(process_count)},
    'LRU': {pid: [] for pid in range(process_count)},
    'OPT': {pid: [] for pid in range(process_count)},
    'RAND': {pid: [] for pid in range(process_count)},
}
#-----------------------------------------------------------------------------------------------

# ZBIERANEI WYNIKÓW
#-----------------------------------------------------------------------------------------------
for vc in physical_capacities:
    fifo_result = fifo_procesowy(copy.deepcopy(requests), vc, process_count, process_proportions)
    sc_result = second_chance_procesowy(copy.deepcopy(requests), vc, process_count, process_proportions)
    lru_result = lru_procesowy(copy.deepcopy(requests), vc, process_count, process_proportions)
    opt_result = opt_procesowy(copy.deepcopy(requests), vc, process_count, process_proportions)
    rand_result = rand_procesowy(copy.deepcopy(requests), vc, process_count, process_proportions)

    # Sumarycznie
    results['FIFO'].append(sum(fifo_result.values()))
    results['SC'].append(sum(sc_result.values()))
    results['LRU'].append(sum(lru_result.values()))
    results['OPT'].append(sum(opt_result.values()))
    results['RAND'].append(sum(rand_result.values()))

    # Per proces
    for pid in range(process_count):
        results_per_process['FIFO'][pid].append(fifo_result[pid])
        results_per_process['SC'][pid].append(sc_result[pid])
        results_per_process['LRU'][pid].append(lru_result[pid])
        results_per_process['OPT'][pid].append(opt_result[pid])
        results_per_process['RAND'][pid].append(rand_result[pid])
#-----------------------------------------------------------------------------------------------

# BŁĘDU SUMARYCZNE, DLA KAŻDEGO ALGORYTMU I ICH WYKRES
#-----------------------------------------------------------------------------------------------
plt.figure(figsize=(10, 6))
for alg in results:
    plt.plot(physical_capacities, results[alg], marker='o', label=alg)

plt.title(" Liczba błędów stron vs. ilość pamięci fizycznej (suma dla wszystkich procesów)")
plt.xlabel("Ilość pamięci fizycznej (virtual_capacity)")
plt.ylabel("Liczba błędów stron")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
#-----------------------------------------------------------------------------------------------

# Wykresy 2-6: dla każdego algorytmu — błędy w zależności od procesu
#-----------------------------------------------------------------------------------------------
for alg, per_process_data in results_per_process.items():
    plt.figure(figsize=(10, 6))
    for pid in range(process_count):
        plt.plot(physical_capacities, per_process_data[pid], marker='o', label=f'P{pid}')
    plt.title(f"📈 Liczba błędów stron – {alg}")
    plt.xlabel("Ilość pamięci fizycznej (virtual_capacity)")
    plt.ylabel("Liczba błędów stron")
    plt.legend(title='Proces')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

