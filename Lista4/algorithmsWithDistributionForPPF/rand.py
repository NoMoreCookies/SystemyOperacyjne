import random
from collections import deque

def rand_ppf_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                      delta_t=100, lower_threshold=0.3, upper_threshold=0.6, high_threshold=0.8):

    # Początkowy przydział ramek
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)

    # Bufor dostępnych ramek — te, które nie są przydzielone
    available_frames = virtual_capacity - sum(process_frame_counts)

    # Inicjalizacja pamięci i liczników błędów
    pamiec_procesow = {p: set() for p in range(process_count)}
    bledy_procesow = {p: 0 for p in range(process_count)}

    # Bufory do obliczania PPF
    recent_faults = {p: deque(maxlen=delta_t) for p in range(process_count)}

    # Flaga wstrzymania procesów
    suspended = {p: False for p in range(process_count)}

    total_requests_sorted = sorted(ciag_odwolan, key=lambda x: x[2])

    log_data = []
    current_time = 0 

    for idx, (process_id, page, time, _) in enumerate(total_requests_sorted):

        if suspended[process_id]:
            recent_faults[process_id].append(0)
        else:
            pamiec = pamiec_procesow[process_id]
            rozmiar_pamieci = process_frame_counts[process_id]

            if page in pamiec:
                recent_faults[process_id].append(0)
            else:
                bledy_procesow[process_id] += 1
                recent_faults[process_id].append(1)

                if len(pamiec) < rozmiar_pamieci:
                    pamiec.add(page)
                else:
                    strona_do_usuniecia = random.choice(list(pamiec))
                    pamiec.remove(strona_do_usuniecia)
                    pamiec.add(page)

            pamiec_procesow[process_id] = pamiec
        
        # Aktualizacja przydziałów co delta_t kroków
        if (idx + 1) % delta_t == 0:
            current_time += delta_t
            for pid in range(process_count):
                frame_action = None
                faults = sum(recent_faults[pid])
                ppf = faults / delta_t

                if ppf > high_threshold and not suspended[pid]:
                    # Wstrzymaj proces
                    suspended[pid] = True
                    available_frames += process_frame_counts[pid]
                    process_frame_counts[pid] = 0
                    pamiec_procesow[pid].clear()
                    frame_action = "suspended"

                elif suspended[pid]:
                    # Sprawdź, czy można wznowić proces (PPF niskie i są wolne ramki)
                    if ppf < lower_threshold and available_frames > 0:
                        suspended[pid] = False
                        przydzial = min(available_frames, max(1, int(virtual_capacity * process_proportions[pid])))
                        process_frame_counts[pid] = przydzial
                        available_frames -= przydzial
                        frame_action = "resumed"

                elif not suspended[pid]:
                    # Dostosuj ramki, jeśli proces nie jest wstrzymany
                    if ppf > upper_threshold:
                        if available_frames > 0:
                            process_frame_counts[pid] += 1
                            available_frames -= 1
                            frame_action = "gained"
                    elif ppf < lower_threshold:
                        if process_frame_counts[pid] > 1:
                            process_frame_counts[pid] -= 1
                            available_frames += 1
                            if pamiec_procesow[pid]:
                                losowa_strona = random.choice(list(pamiec_procesow[pid]))
                                pamiec_procesow[pid].remove(losowa_strona)
                            frame_action = "lost"

                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_ppf': ppf,
                    'allocated_frames': process_frame_counts[pid],
                    'process_suspended': suspended[pid],
                    'frame_action': frame_action
                })

    return bledy_procesow, suspended, log_data
