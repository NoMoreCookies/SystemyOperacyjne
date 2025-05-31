import matplotlib.pyplot as plt
from algorithms.fifo import fifo
from algorithms.opt import opt
from algorithms.rand import rand 
from algorithms.lru import lru 
from algorithms.lfu import  second_chance
from generator import generate_requests

def plot_faults_vs_frames(ciag_odwolan, max_frames):
    fifo_faults = []
    opt_faults = []
    rand_faults = []
    lru_faults = []
    sc_faults = []

    for frames in range(1, max_frames + 1):
        fifo_faults.append(fifo(ciag_odwolan, frames))
        opt_faults.append(opt(ciag_odwolan, frames))
        rand_faults.append(rand(ciag_odwolan, frames))
        lru_faults.append(lru(ciag_odwolan, frames))
        sc_faults.append(second_chance(ciag_odwolan, frames))

    plt.figure(figsize=(10,6))
    plt.plot(range(1, max_frames + 1), fifo_faults, label="FIFO", marker='o')
    plt.plot(range(1, max_frames + 1), opt_faults, label="OPT", marker='o')
    plt.plot(range(1, max_frames + 1), rand_faults, label="RAND", marker='o')
    plt.plot(range(1, max_frames + 1), lru_faults, label="LRU", marker='o')
    plt.plot(range(1, max_frames + 1), sc_faults, label="Second Chance", marker='o')

    plt.xlabel("Liczba ramek")
    plt.ylabel("Liczba błędów stron")
    plt.title("Porównanie algorytmów zarządzania pamięcią")
    plt.legend()
    plt.grid(True)
    plt.show()

# Załóżmy, że masz listę requestów wygenerowaną funkcją generate_requests
# requests = generate_requests(...)

# 1. Generujemy requesty
# 1. Generujemy requesty
requests, frame_alloc = generate_requests(
    process_count=4,
    total_frames=50,
    total_requests=100,
    phases=1,
    process_proportions=[0.8, 0.05, 0.05,0.05]
)

# 2. Ekstrahujemy ciąg stron
ciag_odwolan = [page for (_, page, _, _) in requests]

# 3. Definiujemy maksymalną liczbę ramek (np. 20)
max_frames = 40

# 4. Wywołujemy funkcję rysującą wykres (przykład funkcji z poprzedniego posta)
plot_faults_vs_frames(ciag_odwolan, max_frames)

