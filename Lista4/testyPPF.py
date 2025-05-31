import matplotlib.pyplot as plt
from generator import generate_requests
from ppf import simulate_ppf_control  # zakładam, że tam masz symulację
import numpy as np
import random

def run_test_for_algorithms_and_frames():
    process_count = 4
    total_requests = 200
    phases = 2
    process_proportions = [0.3, 0.3, 0.2, 0.2]
    algorithms = ["fifo", "lru", "opt", "second_chance", "random"]
    max_frames_list = [10, 20, 30, 40, 50]

    # Progowe wartości PPF
    l = 0.1
    u = 0.4
    h = 1
    window_size = 3
    total_frames = 50

    # Miejsce na wyniki - słownik algorytm -> lista błędów dla kolejnych max_frames
    results = {alg: [] for alg in algorithms}

    for max_frames in max_frames_list:
        # Generujemy requesty i przydział ramki (równomiernie do max_frames)
        requests, frame_alloc = generate_requests(process_count, total_frames, total_requests, phases, process_proportions)
        trimmed_requests = [(pid, page) for (pid, page, _, _) in requests]

        for alg in algorithms:
            print(alg)
            print(f"Testuję algorytm {alg} z max_frames={max_frames}")
            # Uruchamiamy symulację PPF
            managers = simulate_ppf_control(
                trimmed_requests.copy(), frame_alloc.copy(), total_frames, process_count,
                l, u, h, window_size, alg
            )

            total_faults = sum(m.total_faults for m in managers)
            results[alg].append(total_faults)

    print(results)
    # Rysowanie wykresu
    plt.figure(figsize=(10,6))
    for alg in algorithms:
        plt.plot(max_frames_list, results[alg], marker='o', label=alg.upper())

    plt.title("Porównanie sumy błędów stron dla różnych algorytmów i liczby ramek (PPF)")
    plt.xlabel("Maksymalna liczba ramek (max_frames)")
    plt.ylabel("Suma błędów stron (page faults)")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    run_test_for_algorithms_and_frames()
