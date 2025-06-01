import random
from collections import deque

def opt_ppf_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                      delta_t=100, lower_threshold=0.1, upper_threshold=0.25, high_threshold=0.5):
    
    # 1. Przydział początkowy ramek (proporcjonalny)
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)

    # 2. Żądania per proces (posortowane wg czasu)
    odwolania_per_process = {p: [] for p in range(process_count)}
    for r in sorted(ciag_odwolan, key=lambda x: x[2]):
        odwolania_per_process[r[0]].append(r)

    # 3. Inicjalizacja
    pamiec_procesow = {p: [] for p in range(process_count)}
    bledy_procesow = {p: 0 for p in range(process_count)}
    recent_faults = {p: deque(maxlen=delta_t) for p in range(process_count)}
    suspended = {p: False for p in range(process_count)}

    # 4. Indeksy wskazujące aktualne żądanie dla każdego procesu
    indices = {p: 0 for p in range(process_count)}
    total_requests_sorted = sorted(ciag_odwolan, key=lambda x: x[2])

    available_frames = 0  # wolne ramki (zwalniane po wstrzymaniu)

    log_data = []
    current_time = 0

    for idx, (process_id, page, time, _) in enumerate(total_requests_sorted):
        page_fault_occurred_per_process = {p: None for p in range(process_count)}

        if suspended[process_id]:
            # Proces wstrzymany — brak błędu
            recent_faults[process_id].append(0)
            page_fault_occurred_per_process[process_id] = False
        else:
            pamiec = pamiec_procesow[process_id]
            rozmiar_pamieci = process_frame_counts[process_id]

            if page in pamiec:
                recent_faults[process_id].append(0)
                page_fault_occurred_per_process[process_id] = False
            else:
                # Błąd strony
                bledy_procesow[process_id] += 1
                recent_faults[process_id].append(1)
                page_fault_occurred_per_process[process_id] = True

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

        # Aktualizacja przydziałów co delta_t odwołań
        if (idx + 1) % delta_t == 0:
            current_time += delta_t
            frame_actions = {p: None for p in range(process_count)}

            for pid in range(process_count):
                faults = sum(recent_faults[pid])
                current_ppf = faults / delta_t

                if suspended[pid]:
                    current_ppf = -1  # oznaczamy zawieszony proces

                if not suspended[pid]:
                    # Decyzje o zawieszeniu i alokacji
                    if current_ppf > high_threshold:
                        suspended[pid] = True
                        available_frames += process_frame_counts[pid]
                        process_frame_counts[pid] = 0
                        frame_actions[pid] = "suspended"

                        # Wyczyszczenie pamięci procesu (wolne ramki)
                        pamiec_procesow[pid].clear()

                    elif current_ppf > upper_threshold and available_frames == 0:
                        suspended[pid] = True
                        available_frames += process_frame_counts[pid]
                        process_frame_counts[pid] = 0
                        frame_actions[pid] = "suspended"

                        pamiec_procesow[pid].clear()

                    elif current_ppf > upper_threshold:
                        if available_frames > 0:
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

                # Logowanie dla każdego procesu
                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_ppf': current_ppf,
                    'allocated_frames': process_frame_counts[pid],
                    'page_fault_occurred': page_fault_occurred_per_process[pid],
                    'process_suspended': suspended[pid],
                    'frame_action': frame_actions[pid]
                })

    return bledy_procesow, suspended, log_data
