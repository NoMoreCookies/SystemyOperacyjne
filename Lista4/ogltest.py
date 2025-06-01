def run_lru_only_test():
    import copy
    import matplotlib.pyplot as plt
    from generator import generate_requests

    from algorithmsWWS.lru import lru_wws_procesowy
    from algorithmsWithDistrubution.lru import lru_procesowy
    from equalAlgorithms.lru import lru_procesowy1
    from algorithmsWithDistributionForPPF.lru import lru_ppf_procesowy_z_logiem

    # Parametry
    process_count = 3
    total_frames = 300
    total_requests = 1000
    phases = 2
    process_proportions = [0.6, 0.2, 0.2]

    # Generowanie wspólnego zestawu odwołań
    requests, _ = generate_requests(
        process_count=process_count,
        total_frames=total_frames,
        total_requests=total_requests,
        phases=phases,
        process_proportions=process_proportions
    )

    virtual_capacities = range(30, 126, 1)

    combined_results = {
        "Przydział równy": [],
        "Przydział proporcjonalny": [],
        "Sterowanie częstością błędów": [],
        "Model strefowy": [],
    }

    # --- 1) Przydział równy ---
    for vc in virtual_capacities:
        faults = lru_procesowy1(copy.deepcopy(requests), vc, process_count, process_proportions)
        combined_results["Przydział równy"].append(sum(faults.values()))

    # --- 2) Przydział proporcjonalny ---
    for vc in virtual_capacities:
        faults = lru_procesowy(copy.deepcopy(requests), vc, process_count, process_proportions)
        combined_results["Przydział proporcjonalny"].append(sum(faults.values()))

    # --- 3) Sterowanie częstością błędów ---
    for vc in virtual_capacities:
        faults, _, _ = lru_ppf_procesowy_z_logiem(
            ciag_odwolan=copy.deepcopy(requests),
            virtual_capacity=vc,
            process_count=process_count,
            process_proportions=process_proportions
        )
        combined_results["Sterowanie częstością błędów"].append(sum(faults.values()))

    # --- 4) Model strefowy ---
    for vc in virtual_capacities:
        faults, _, _ = lru_wws_procesowy(
            ciag_odwolan=copy.deepcopy(requests),
            virtual_capacity=vc,
            process_count=process_count,
            process_proportions=process_proportions,
            delta_t=100,
            c_factor=0.5
        )
        combined_results["Model strefowy"].append(sum(faults.values()))

    # Wykres
    plt.figure(figsize=(12, 7))
    for method, faults in combined_results.items():
        plt.plot(virtual_capacities, faults, label=method)
    plt.title("Porównanie LRU – suma błędów stron dla różnych metod przydziału ramek")
    plt.xlabel("Pojemność pamięci fizycznej (liczba ramek)")
    plt.ylabel("Suma błędów stron")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_lru_only_test()
