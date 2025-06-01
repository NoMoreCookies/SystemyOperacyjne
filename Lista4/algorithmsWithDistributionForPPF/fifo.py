import random
from collections import deque

def fifo_ppf_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                       delta_t=100, lower_threshold=0.1, upper_threshold=0.25, high_threshold=0.5):

    current_time = 0 
    # Przydział ramek na podstawie proporcji, zaokrąglony w dół, potem reszta do pierwszego
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)
    
    # Liczba dostępnych ramek (wolnych) początkowo zero, bo wszystkie rozdysponowane
    available_frames = 0
    
    # Pamięć każdego procesu jako deque do FIFO
    pamiec_procesow = {p: deque() for p in range(process_count)}
    
    # Liczba błędów stron na proces
    bledy_procesow = {p: 0 for p in range(process_count)}
    
    # Ostatnie delta_t błędów (1=błąd, 0=trafienie) do obliczania PPF
    recent_faults = {p: deque(maxlen=delta_t) for p in range(process_count)}
    
    # Status zawieszenia procesów
    suspended = {p: False for p in range(process_count)}
    
    # Logi do śledzenia przebiegu
    log_data = []
    
    # Aktualny PPF procesów
    current_ppf = {p: 0.0 for p in range(process_count)}
    
    for idx, (process_id, page, time, _) in enumerate(sorted(ciag_odwolan, key=lambda x: x[2])):
        page_fault_occurred = {p: None for p in range(process_count)}  # Błąd strony dla każdego procesu w tym kroku
        
        if suspended[process_id]:
            # Proces zawieszony - ignorujemy jego odwołanie, brak błędu
            page_fault_occurred[process_id] = False
        else:
            memory = pamiec_procesow[process_id]
            frame_limit = process_frame_counts[process_id]
            
            if page in memory:
                # Trafienie - strona jest już w pamięci
                page_fault_occurred[process_id] = False
                recent_faults[process_id].append(0)
            else:
                # Błąd strony
                page_fault_occurred[process_id] = True
                bledy_procesow[process_id] += 1
                recent_faults[process_id].append(1)
                
                if len(memory) < frame_limit:
                    memory.append(page)
                else:
                    if memory:
                        memory.popleft()  # FIFO - usuwamy najstarszą stronę
                    memory.append(page)
        
        # Co delta_t - obliczamy PPF i modyfikujemy alokację ramek
        if (idx + 1) % delta_t == 0:
            current_time += delta_t
            
            for pid in range(process_count):
                if suspended[pid]:
                    current_ppf[pid] = -1  # zawieszony proces ma PPF -1
                else:
                    faults = sum(recent_faults[pid])
                    current_ppf[pid] = faults / delta_t
                    
                    if current_ppf[pid] > high_threshold:
                        # Zawieszamy proces
                        suspended[pid] = True
                        available_frames += process_frame_counts[pid]
                        process_frame_counts[pid] = 0
                    
                    elif current_ppf[pid] > upper_threshold:
                        if available_frames > 0:
                            process_frame_counts[pid] += 1
                            available_frames -= 1
                        else:
                            # Brak wolnych ramek, zawieszamy proces
                            suspended[pid] = True
                            available_frames += process_frame_counts[pid]
                            process_frame_counts[pid] = 0
                    
                    elif current_ppf[pid] < lower_threshold:
                        if process_frame_counts[pid] > 1:  # minimum 1 ramka, by nie zabrać wszystkiego
                            process_frame_counts[pid] -= 1
                            available_frames += 1
                            if pamiec_procesow[pid]:
                                pamiec_procesow[pid].popleft()  # usuwamy najstarszą stronę
    
            # Logowanie stanu
            for pid in range(process_count):
                if suspended[pid]:
                    action = "suspended"
                elif current_ppf[pid] > upper_threshold:
                    action = "gained"
                elif current_ppf[pid] < lower_threshold:
                    action = "lost"
                else:
                    action = None
                
                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_ppf': current_ppf[pid],
                    'allocated_frames': process_frame_counts[pid],
                    'page_fault_occurred': page_fault_occurred[pid],
                    'process_suspended': suspended[pid],
                    'frame_action': action
                })
    
    return bledy_procesow, suspended, log_data
