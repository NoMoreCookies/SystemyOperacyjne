import random
from collections import deque

def opt_ppf_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                      delta_t=100, lower_threshold=0.1, upper_threshold=0.25, high_threshold=0.5):
    
    #-----------------------------------------------------------------------------------------------
    # 1. Przydział początkowy ramek
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)

    # 2. Wyodrębnij żądania per proces
    odwolania_per_process = {p: [] for p in range(process_count)}
    for r in sorted(ciag_odwolan, key=lambda x: x[2]):
        odwolania_per_process[r[0]].append(r)

    # 3. Inicjalizacja
    pamiec_procesow = {p: [] for p in range(process_count)}
    bledy_procesow = {p: 0 for p in range(process_count)}

    # 4. Do śledzenia PPF
    recent_requests = {p: deque(maxlen=delta_t) for p in range(process_count)}
    recent_faults = {p: deque(maxlen=delta_t) for p in range(process_count)}

    # 5. Globalna pula dostępnych ramek
    available_frames = 0

    # Flaga wstrzymania procesów
    suspended = {p: False for p in range(process_count)}

    # 6. Indeksy dla każdego procesu w jego liście żądań
    indices = {p: 0 for p in range(process_count)}
    total_requests_sorted = sorted(ciag_odwolan, key=lambda x: x[2])
    

    log_data = []
    current_time = 0
    #-----------------------------------------------------------------------------------------------

    #-----------------------------------------------------------------------------------------------
    for idx, (process_id, page, time, _) in enumerate(total_requests_sorted):
        page_fault_occurred = False  # domyślnie
        # Pomijamy wstrzymane procesy
        if suspended[process_id]:
            # nawet jeśli proces wstrzymany, rejestrujemy brak błędu
            recent_faults[process_id].append(0)
        else:
            pamiec = pamiec_procesow[process_id]
            rozmiar_pamieci = process_frame_counts[process_id]

            # Rejestracja żądania


            # Sprawdź, czy strona jest w pamięci
            if page in pamiec:
                recent_faults[process_id].append(0)
            else:
                # Błąd strony
                bledy_procesow[process_id] += 1
                recent_faults[process_id].append(1)
                page_fault_occurred = True

                if len(pamiec) < rozmiar_pamieci:
                    pamiec.append(page)
                else:
                    odwolania = odwolania_per_process[process_id]
                    current_index = indices[process_id]

                    przyszle = [odw[1] for odw in odwolania[current_index+1:]]
                    indeksy = []
                    for s in pamiec:
                        try:
                            indeksy.append(przyszle.index(s))
                        except ValueError:
                            indeksy.append(float('inf'))

                    index_do_usuniecia = indeksy.index(max(indeksy))
                    pamiec[index_do_usuniecia] = page

            pamiec_procesow[process_id] = pamiec

        indices[process_id] += 1
    #-----------------------------------------------------------------------------------------------

        # Aktualizacja przydziałów co delta_t kroków
        if (idx + 1) % delta_t == 0:

            current_time += delta_t
            frame_actions = {p: None for p in range(process_count)}

            for pid in range(process_count):
                faults = sum(recent_faults[pid])

                current_ppf = faults / delta_t

                # Wstrzymanie procesu
                if current_ppf > high_threshold :
                    suspended[pid] = True
                    available_frames += process_frame_counts[pid]
                    process_frame_counts[pid] = 0
                    frame_actions[pid] = "suspended"
                elif current_ppf > upper_threshold and available_frames==0:
                    suspended[pid] = True
                    available_frames += process_frame_counts[pid]
                    process_frame_counts[pid] = 0
                    frame_actions[pid] = "suspended"
                elif current_ppf > upper_threshold:
                        process_frame_counts[pid] += 1
                        available_frames -= 1
                        frame_actions[pid] = "gained"
                elif current_ppf < lower_threshold:
                        if process_frame_counts[pid] > 1:
                            process_frame_counts[pid] -= 1
                            available_frames += 1
                            if pamiec_procesow[pid]:
                                losowa_strona = random.choice(pamiec_procesow[pid])
                                pamiec_procesow[pid].remove(losowa_strona)
                            frame_actions[pid] = "lost"

                # Logowanie dla każdego procesu na tym etapie
                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_ppf': current_ppf,
                    'allocated_frames': process_frame_counts[pid],
                    'page_fault_occurred': page_fault_occurred if pid == process_id else None,
                    'process_suspended': suspended[pid],
                    'frame_action': frame_actions[pid]
                })
            

    return bledy_procesow, suspended, log_data
