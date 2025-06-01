import random
from collections import deque

def second_chance_ppf_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                                 delta_t=100, lower_threshold=0.1, upper_threshold=0.25, high_threshold=0.5):

    # Przydział początkowy ramek (proporcjonalny)
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)
    
    # Struktury danych
    pamiec_procesow = {p: deque() for p in range(process_count)}  # kolekcja stron FIFO
    bity_procesow = {p: {} for p in range(process_count)}        # bit użycia second chance
    bledy_procesow = {p: 0 for p in range(process_count)}
    recent_faults = {p: deque(maxlen=delta_t) for p in range(process_count)}
    suspended = {p: False for p in range(process_count)}
    
    # Na start wolnych ramek brak, bo rozdysponowane
    available_frames = 0
    
    current_ppf = {p: 0.0 for p in range(process_count)}
    current_time = 0
    log_data = []
    frame_actions = {p: None for p in range(process_count)}

    for idx, (process_id, page, time, _) in enumerate(sorted(ciag_odwolan, key=lambda x: x[2])):
        page_fault_occurred_per_process = {p: None for p in range(process_count)}
        
        if suspended[process_id]:
            # Proces zatrzymany — brak błędu i żadnej zmiany
            page_fault_occurred_per_process[process_id] = False
        else:
            pamiec = pamiec_procesow[process_id]
            bity = bity_procesow[process_id]
            frame_limit = process_frame_counts[process_id]
            
            if page in bity:
                # Strona jest w pamięci - ustawiamy bit użycia
                bity[page] = 1
                page_fault_occurred_per_process[process_id] = False
                recent_faults[process_id].append(0)
            else:
                # Błąd strony
                bledy_procesow[process_id] += 1
                recent_faults[process_id].append(1)
                page_fault_occurred_per_process[process_id] = True
                
                if len(pamiec) < frame_limit:
                    pamiec.append(page)
                    bity[page] = 1
                else:
                    # Algorytm Second Chance - szukamy strony do usunięcia
                    while True:
                        oldest = pamiec[0]
                        if bity[oldest] == 0:
                            pamiec.popleft()
                            del bity[oldest]
                            break
                        else:
                            pamiec.popleft()
                            pamiec.append(oldest)
                            bity[oldest] = 0
                    pamiec.append(page)
                    bity[page] = 1
        
        # Co delta_t odwołań obliczamy PPF i modyfikujemy alokację ramek
        if (idx + 1) % delta_t == 0 and idx > 0:
            current_time += delta_t
            frame_actions = {p: None for p in range(process_count)}
            
            for pid in range(process_count):
                if suspended[pid]:
                    current_ppf[pid] = -1
                else:
                    faults = sum(recent_faults[pid])
                    current_ppf[pid] = faults / delta_t
                    
                    if current_ppf[pid] > high_threshold:
                        # Zawieszamy proces
                        suspended[pid] = True
                        available_frames += process_frame_counts[pid]
                        process_frame_counts[pid] = 0
                        frame_actions[pid] = "suspended"
                    
                    elif current_ppf[pid] > upper_threshold and available_frames == 0:
                        # Zawieszamy proces (brak wolnych ramek)
                        suspended[pid] = True
                        available_frames += process_frame_counts[pid]
                        process_frame_counts[pid] = 0
                        frame_actions[pid] = "suspended"
                    
                    elif current_ppf[pid] > upper_threshold:
                        if available_frames > 0:
                            process_frame_counts[pid] += 1
                            available_frames -= 1
                            frame_actions[pid] = "gained"
                    
                    elif current_ppf[pid] < lower_threshold:
                        if process_frame_counts[pid] > 1:  # minimum 1 ramka
                            process_frame_counts[pid] -= 1
                            available_frames += 1
                            # Usuwamy losową stronę i jej bit użycia
                            if pamiec_procesow[pid]:
                                to_remove = random.choice(list(pamiec_procesow[pid]))
                                pamiec_procesow[pid].remove(to_remove)
                                if to_remove in bity_procesow[pid]:
                                    del bity_procesow[pid][to_remove]
                            frame_actions[pid] = "lost"
            
            # Logowanie dla każdego procesu
            for pid in range(process_count):
                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_ppf': current_ppf[pid],
                    'allocated_frames': process_frame_counts[pid],
                    'page_fault_occurred': page_fault_occurred_per_process[pid],
                    'process_suspended': suspended[pid],
                    'frame_action': frame_actions[pid]
                })
    
    return bledy_procesow, suspended, log_data
