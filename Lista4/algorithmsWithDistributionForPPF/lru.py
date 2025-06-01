import random
from collections import deque

def lru_ppf_procesowy_z_logiem(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                                delta_t=100, lower_threshold=0.3, upper_threshold=0.6, high_threshold=0.8,
                                min_frames=2):

    # Inicjalizacja liczby ramek dla każdego procesu - minimalnie min_frames, reszta proporcjonalnie
    process_frame_counts = [max(int(virtual_capacity * p), min_frames) for p in process_proportions]
    # Dopasowujemy sumę ramek do całkowitej pojemności pamięci wirtualnej
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)

    # Słownik pamięci procesów: {proces_id: {strona: wiek strony (czas od ostatniego użycia)}}
    pamiec_procesow = {p: {} for p in range(process_count)}

    # Liczba błędów stron dla każdego procesu
    bledy_procesow = {p: 0 for p in range(process_count)}

    # Kolejki (okna) ostatnich żądań i błędów stron dla każdego procesu (używane do obliczania PPF)
    recent_requests = {p: deque(maxlen=delta_t) for p in range(process_count)}
    recent_faults = {p: deque(maxlen=delta_t) for p in range(process_count)}

    # Status zawieszenia procesów (True = proces zawieszony)
    suspended = {p: False for p in range(process_count)}

    # Zapamiętujemy ile ramek miał proces w momencie zawieszenia (do odwieszenia)
    zawieszone_ramki = {p: 0 for p in range(process_count)}

    # Liczba dostępnych ramek (wolnych) w systemie, które mogą być przydzielone procesom
    available_frames = 0

    # Lista logów z informacjami o stanie systemu w czasie
    log_data = []

    # Aktualny czas symulacji (liczony co delta_t)
    current_time = 0

    # Aktualna wartość PPF dla każdego procesu
    current_ppf = {p: 0.0 for p in range(process_count)}

    # Pętla po wszystkich odwołaniach (posortowanych wg czasu)
    for idx, (process_id, page, time, _) in enumerate(sorted(ciag_odwolan, key=lambda x: x[2])):

        # Inicjujemy słownik błędów dla każdego procesu na ten krok
        page_fault_occurred = {pid: False for pid in range(process_count)}

        # Jeśli proces jest zawieszony - nie obsługujemy jego żądań (nie zwiększamy pamięci)
        if suspended[process_id]:
            recent_requests[process_id].append(0)  # brak żądania (proces "nieaktywny")
        else:
            # Proces jest aktywny, dodajemy żądanie
            recent_requests[process_id].append(1)

            # Pobieramy pamięć i limit ramek dla tego procesu
            pamiec = pamiec_procesow[process_id]
            frame_limit = process_frame_counts[process_id]

            # Zwiększamy "wiek" wszystkich stron w pamięci (liczymy, ile od ostatniego użycia)
            for s in pamiec:
                pamiec[s] += 1

            # Sprawdzamy czy strona jest już w pamięci
            if page in pamiec:
                pamiec[page] = 0  # resetujemy wiek strony (bo użyta)
                recent_faults[process_id].append(0)  # brak błędu strony
            else:
                # Błąd strony - strona nie jest w pamięci
                bledy_procesow[process_id] += 1
                recent_faults[process_id].append(1)  # zapamiętujemy błąd

                # Dodajemy stronę do pamięci (jeśli jest miejsce)
                if len(pamiec) < frame_limit:
                    pamiec[page] = 0
                else:
                    # Brak miejsca - usuwamy najstarszą stronę (LRU)
                    to_remove = max(pamiec.items(), key=lambda x: x[1])[0]
                    del pamiec[to_remove]
                    pamiec[page] = 0

        # Co delta_t - aktualizacja alokacji ramek i stanów procesów
        if (idx + 1) % delta_t == 0:
            current_time += delta_t  # zwiększamy "czas symulacji"
            frame_actions = {p: None for p in range(process_count)}  # resetujemy akcje na ten krok

            for pid in range(process_count):
                if suspended[pid]:
                    # Jeśli proces zawieszony - PPF ustawiamy na -1 (nieaktywny)
                    current_ppf[pid] = -1
                else:
                    # Obliczamy PPF = liczba błędów stron / liczba żądań
                    requests = sum(recent_requests[pid])
                    faults = sum(recent_faults[pid])
                    current_ppf[pid] = (faults / requests) if requests > 0 else 0.0

                    # Podejmujemy decyzje na podstawie PPF i progów
                    if current_ppf[pid] > high_threshold:
                        # Jeśli jest wystarczająco dużo aktywnych procesów, zawieszamy proces z wysokim PPF
                        if sum(not suspended[p] for p in suspended) > 1:
                            suspended[pid] = True
                            zawieszone_ramki[pid] = process_frame_counts[pid]  # zapamiętujemy ile miał ramek
                            available_frames += process_frame_counts[pid]     # oddajemy jego ramki do puli
                            process_frame_counts[pid] = 0                      # proces traci ramki
                            pamiec_procesow[pid].clear()                       # czyscimy jego pamięć
                            frame_actions[pid] = "suspended"

                    elif current_ppf[pid] > upper_threshold:
                        # Gdy PPF przekracza górny próg, próbujemy zwiększyć ramki jeśli mamy wolne
                        if available_frames > 0:
                            process_frame_counts[pid] += 1
                            available_frames -= 1
                            frame_actions[pid] = "gained"
                        # Jeśli nie ma wolnych ramek i jest więcej niż jeden aktywny proces, zawieszamy ten proces
                        elif sum(not suspended[p] for p in suspended) > 1:
                            suspended[pid] = True
                            zawieszone_ramki[pid] = process_frame_counts[pid]
                            available_frames += process_frame_counts[pid]
                            process_frame_counts[pid] = 0
                            pamiec_procesow[pid].clear()
                            frame_actions[pid] = "suspended"

                    elif current_ppf[pid] < lower_threshold:
                        # Jeśli PPF jest bardzo niski, zmniejszamy liczbę ramek przydzielonych procesowi
                        if process_frame_counts[pid] > min_frames:
                            process_frame_counts[pid] -= 1
                            available_frames += 1
                            # Usuwamy losową stronę z pamięci (bo mniej ramek)
                            if pamiec_procesow[pid]:
                                to_remove = random.choice(list(pamiec_procesow[pid].keys()))
                                del pamiec_procesow[pid][to_remove]
                            frame_actions[pid] = "lost"

            # Próba odwieszenia procesów jeśli jest wystarczająco wolnych ramek
            for pid in range(process_count):
                if suspended[pid]:
                    needed = zawieszone_ramki[pid]  # ile ramek potrzebuje do wznowienia
                    if available_frames >= needed:
                        suspended[pid] = False
                        process_frame_counts[pid] = needed
                        available_frames -= needed
                        zawieszone_ramki[pid] = 0
                        frame_actions[pid] = "resumed"

            # Logowanie stanu dla każdego procesu (PPF, liczba ramek, błędy, zawieszenie, akcje)
            for pid in range(process_count):
                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_ppf': current_ppf[pid],
                    'allocated_frames': process_frame_counts[pid],
                    'page_fault_occurred': page_fault_occurred[pid],
                    'process_suspended': suspended[pid],
                    'frame_action': frame_actions[pid]
                })

    # Zwracamy słownik z błędami, stan zawieszenia i logi
    return bledy_procesow, suspended, log_data
