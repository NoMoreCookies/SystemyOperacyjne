import random
from collections import deque
from generator import generate_requests
from utils import ProcessMemoryManager
from utils import FIFO
from utils import OPT
from utils import LRU
from utils import RandomAlg
from utils import SecondChance



# --- Symulacja z sterowaniem PPF ---
#------------------------------------------------
def simulate_ppf_control(requests,frame_alloc, total_frames, process_count, l, u, h, window_size, chosen_algorithm):
    # Słownik mapujący nazwy algorytmów na klasy implementujące je
    algorithms = {
        "fifo": FIFO,
        "second_chance": SecondChance,
        "lru": LRU,
        "opt": OPT,
        "random": RandomAlg
    }
    # Sprawdzenie, czy wybrany algorytm jest znany
    if chosen_algorithm not in algorithms:
        raise ValueError(f"Nieznany algorytm: {chosen_algorithm}")

    # Pobranie klasy algorytmu na podstawie nazwy
    AlgorithmClass = algorithms[chosen_algorithm]



    # Tworzymy menedżerów pamięci dla każdego procesu
    # Każdy menedżer inicjalizowany jest z odpowiednią liczbą ramek i wybranym algorytmem
    managers = [ProcessMemoryManager(pid=p, init_frames=frame_alloc[p], window_size=window_size,
                                     AlgorithmClass=AlgorithmClass, all_requests=requests)
                for p in range(process_count)]

    free_frames = 0  # Liczba ramek dostępnych do dynamicznego przydziału

    # Główna pętla symulacji - iterujemy po wszystkich żądaniach stron
    for time, (pid, page) in enumerate(requests):
        manager = managers[pid]  # Pobieramy menedżera pamięci dla procesu, który robi request

        # Jeśli proces jest wstrzymany, pomijamy jego zapytanie i wyświetlamy info
        if manager.paused:
            print(f"[T={time}] Proces P{pid} wstrzymany — pomijanie zapytania.")
            continue

        # Obsługa requestu strony w menedżerze pamięci
        fault = manager.handle_request(page, time)
        # Pobieramy aktualną wartość PPF (page fault frequency)
        ppf = manager.get_ppf()

        # Wyświetlamy informację o żądaniu, błędzie strony, PPF i aktualnej liczbie ramek
        print(f"[T={time}] P{pid} żąda strony {page} | Błąd: {fault} | PPF={ppf:.2f} | Ramki: {manager.frames}")

        # Sterowanie liczbą ramek na podstawie progów PPF:

        # Jeśli PPF przekracza górny próg h, wstrzymujemy proces i zwalniamy jego ramki
        if ppf > h:
            manager.paused = True
            free_frames += manager.frames
            print(f"  -> WSTRZYMANIE procesu P{pid} (PPF={ppf:.2f} > h={h})")
            continue

        # Jeśli PPF jest powyżej progu u, ale poniżej h i są wolne ramki,
        # zwiększamy liczbę ramek przydzielonych procesowi o 1
        if ppf > u:
            if free_frames > 0:
                manager.update_frames(manager.frames + 1, AlgorithmClass)
                free_frames -= 1
                print(f"  -> P{pid} otrzymał dodatkową ramkę (PPF={ppf:.2f} > u={u})")

        # Jeśli PPF jest poniżej dolnego progu l i proces ma więcej niż 1 ramkę,
        # zmniejszamy liczbę ramek przydzielonych procesowi o 1 i zwalniamy tę ramkę
        elif ppf < l:
            if manager.frames > 1:
                manager.update_frames(manager.frames - 1, AlgorithmClass)
                free_frames += 1
                print(f"  -> P{pid} oddał jedną ramkę (PPF={ppf:.2f} < l={l})")

    # Po zakończeniu symulacji wyświetlamy podsumowanie statystyk dla każdego procesu
    print("\n--- Statystyki końcowe ---")
    for m in managers:
        status = "wstrzymany" if m.paused else "aktywny"
        print(f"P{m.pid}: Błędy stron = {m.total_faults}, Ramki = {m.frames}, Status = {status}")
        
    return managers

#------------------------------------------------
