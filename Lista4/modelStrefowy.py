from collections import defaultdict, deque
from generator import generate_requests
from utils import ProcessMemoryManager
from utils import FIFO
from utils import OPT
from utils import LRU
from utils import RandomAlg
from utils import SecondChance

# MODEL STREFOWY 
#------------------------------------------------
def simulate_working_set_with_algorithm(requests, frame_alloc, total_frames, delta_t, c, chosen_algorithm):
    
    """
    requests: lista krotek (pid, page, time, phase)
    frame_alloc: lista liczby ramek przypisanych do procesów
    total_frames: łączna liczba ramek w systemie
    delta_t: okno czasu do wyznaczania WSS
    c: krok aktualizacji WSS (interwał czasu)
    chosen_algorithm: nazwa algorytmu ("fifo", "lru", "opt", itd.)
    """
    # SPRAWDZAM CZY PODANY ALGORYTM MA SENS
    #------------------------------------------------
    algorithms = {
        "fifo": FIFO,
        "second_chance": SecondChance,
        "lru": LRU,
        "opt": OPT,
        "random": RandomAlg
    }
    if chosen_algorithm not in algorithms:
        raise ValueError(f"Nieznany algorytm: {chosen_algorithm}")
    AlgorithmClass = algorithms[chosen_algorithm]
    #------------------------------------------------

    # ZBIERAM PROCESY I USTAWIAM, ŻE WSZYSTKIE SĄ AKTYWNE
    #------------------------------------------------
    pids = set(req[0] for req in requests)
    active = {pid: True for pid in pids}
    #------------------------------------------------

    #GRUPUJE REQUESTY PROCESAMI
    #------------------------------------------------

    # Grupujemy żądania stron według PID procesu: {pid: [(czas, strona), ...]}
    requests_by_pid = defaultdict(list)
    for pid, page, time, phase in requests:
        requests_by_pid[pid].append((time, page))

    # Wyznaczamy maksymalny czas pojawienia się żądania.
    # Jest to koniec symulacji – po tym czasie nie ma już nowych żądań,
    # więc nie trzeba kontynuować przetwarzania.
    max_time = max(req[2] for req in requests)

    # Inicjalizujemy zmienną czasu symulacji od zera.
    time = 0

    # Długość kroku czasowego (np. co ile jednostek czasu przesuwamy symulację).
    # Zmienna `c` to parametr algorytmu, który określa częstotliwość aktualizacji stanu.
    step = c

    #------------------------------------------------

    # TWORZĘ MANAGERY PAMIĘCI DO KAŻDEGO PROCESU
    #------------------------------------------------
    managers = {}
    for pid in pids:
        managers[pid] = ProcessMemoryManager(
            pid=pid,
            init_frames=frame_alloc[pid],  # Początkowa liczba ramek dla procesu
            window_size=delta_t,           # Rozmiar okna czasowego (delta_t) do liczenia WSS
            AlgorithmClass=AlgorithmClass, # Algorytm zarządzania stronami (np. LRU, FIFO)
            all_requests=requests          # Wszystkie żądania (dla algorytmu OPT)
        )
    #------------------------------------------------
    

    #INICJALIZACJA TABLIC, DO KTÓRYCH BĘDZIEMY ZAPISYWAĆ DANE
    #------------------------------------------------
    suspensions = []
    szamotanie_detected_times = []
    #------------------------------------------------

    # Główna pętla symulacji (No ogl po czasie)
    #------------------------------------------------
    while time <= max_time:
        
        #OGARNIANE WSS
        #------------------------------------------------
        WSS = {}           # Working Set Size dla każdego procesu
        total_WSS = 0      # Suma WSS wszystkich aktywnych procesów
        #------------------------------------------------

        # Oblicz WSS dla każdego procesu
        #------------------------------------------------
        for pid in pids:
            if not active[pid]:          # Jeśli proces jest wstrzymany, jego WSS = 0 (NO BO NIE MA ZAPOTRZEBOWANIA)
                WSS[pid] = 0
                continue
            
            #ZBIÓR STRON, DO KTÓRYCH DANY PROCESS UZYSKIWAŁ W DANYM PRZEDZIALE CZASOWYM
            #------------------------------------------------
            pages_in_window = set()      
            for t, page in requests_by_pid[pid]:
                if time - delta_t < t <= time:
                    pages_in_window.add(page)
            WSS[pid] = len(pages_in_window)
            total_WSS += WSS[pid]        # Sumujemy WSS do całkowitego WSS
            #------------------------------------------------

        print(f"Time={time}, Total WSS={total_WSS}, Total frames={total_frames}")

        # Obsługa żądań stron w ramach aktualnego okna czasowego
        for pid in pids:
            status = "Active" if active[pid] else "Suspended"
            print(f" Process {pid}: WSS={WSS[pid]}, Status={status}")

            if active[pid]:
                for t, page in requests_by_pid[pid]:
                    if time - delta_t < t <= time:
                        # Przekazanie strony do menedżera procesu — aktualizuje algorytm zarządzania stronami
                        managers[pid].handle_request(page, t)

        # Wykrywanie szamotania
        e = 0.5 * total_frames  # Próg szamotania (np. połowa dostępnych ramek)
        if total_WSS > e:
            print(f"  -- Szamotanie wykryte przy time={time} (WSS={total_WSS} > e={e})")
            szamotanie_detected_times.append(time)

        # Wstrzymywanie procesów, jeśli całkowite WSS przekracza liczbę dostępnych ramek
        if total_WSS > total_frames:
            # Wybieramy proces do wstrzymania: ten z największym WSS
            candidates = [(pid, wss) for pid, wss in WSS.items() if active[pid]]
            if candidates:
                to_suspend = max(candidates, key=lambda x: x[1])[0]
                active[to_suspend] = False
                suspensions.append((time, to_suspend))  # Rejestrujemy moment wstrzymania
                print(f"  -- Wstrzymano proces {to_suspend} o WSS={WSS[to_suspend]}")

        # Przechodzimy do kolejnego kroku czasowego
        time += step

    #------------------------------------------------

    print("\nStatystyki:")
    print(f"Procesy wstrzymane (czas, pid): {suspensions}")
    print(f"Czasy wykrytego szamotania: {szamotanie_detected_times}")

    # Podsumowanie błędów stron i liczby ramek na koniec
    for pid in pids:
        m = managers[pid]
        status = "wstrzymany" if not active[pid] else "aktywny"
        print(f"P{pid}: Błędy stron = {m.total_faults}, Ramki = {m.frames}, Status = {status}")





if __name__ == "__main__":
    # --- Test --- Jeszcze przeanalizuj czy na pewno działa poprawnie twoim zdaniem
    #------------------------------------------------------------------------------------------
    process_count = 4
    total_frames = 40
    total_requests = 100
    phases = 2
    process_proportions = [0.3, 0.3, 0.2, 0.2]
    requests, frame_alloc = generate_requests(process_count, total_frames, total_requests, phases, process_proportions)
    trimmed_requests = [(pid, page) for (pid, page, _, _) in requests]

    simulate_working_set_with_algorithm(
        requests=requests,
        frame_alloc=frame_alloc,
        total_frames=20,
        delta_t=10,
        c=5,
        chosen_algorithm="fifo"  # lub "lru", "opt", "second_chance", "random"
    )