import matplotlib.pyplot as plt
from generator import generate_requests
from algorithmsWWS.lfu import second_chance_wws_procesowy
from algorithmsWWS.fifo import fifo_wws_procesowy
from algorithmsWWS.lru import lru_wws_procesowy
from algorithmsWWS.opt import opt_wws_procesowy
from algorithmsWWS.rand import rand_wws_procesowy

def run_comparison():
    # Parametry
    process_count = 3
    total_frames = 150
    total_requests = 1000
    phases = 3
    process_proportions = [0.5, 0.3, 0.2]

    # Generowanie odwołań
    requests, _ = generate_requests(
        process_count=process_count,
        total_frames=total_frames,
        total_requests=total_requests,
        phases=phases,
        process_proportions=process_proportions
    )

    # Algorytmy do testowania
    wws_algorithms = {
        "Second_Chance_WWS": second_chance_wws_procesowy,
        "FIFO_WWS": fifo_wws_procesowy,
        "LRU_WWS": lru_wws_procesowy,
        "OPT_WWS": opt_wws_procesowy,
        "RAND_WWS": rand_wws_procesowy,
    }

    virtual_capacities = list(range(20, 200, 1)) 

    results = {name: [] for name in wws_algorithms}

    for vc in virtual_capacities:
        print(f"Testuję pojemność: {vc}")
        for name, alg in wws_algorithms.items():
            bledy, suspended, log = alg(
                ciag_odwolan=requests,
                virtual_capacity=vc,
                process_count=process_count,
                process_proportions=process_proportions,
                delta_t=10,
                c_factor=0.5
            )
            total_faults = sum(bledy.values())
            results[name].append(total_faults)

    # Rysowanie wykresu
    plt.figure(figsize=(12, 6))
    for name, faults in results.items():
        plt.plot(virtual_capacities, faults, marker='o', label=name)

    plt.title("Porównanie liczby błędów stron dla algorytmów WWS")
    plt.xlabel("Pojemność pamięci wirtualnej (liczba ramek)")
    plt.ylabel("Liczba błędów stron")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_comparison()
