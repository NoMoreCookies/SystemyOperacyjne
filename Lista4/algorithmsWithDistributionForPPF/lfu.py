import random
from collections import deque

def second_chance_ppf_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                                 delta_t=100, lower_threshold=0.1, upper_threshold=0.25, high_threshold=0.5):
    
    # Startowy proporcjonalny przydział ramek
    #-----------------------------------------------------------------------------------------------
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)
    #-----------------------------------------------------------------------------------------------

    # Inicjalizacja struktur danych
    #-----------------------------------------------------------------------------------------------
    pamiec_procesow = {p: deque() for p in range(process_count)}
    bity_procesow = {p: {} for p in range(process_count)}
    bledy_procesow = {p: 0 for p in range(process_count)}

    recent_faults = {p: deque(maxlen=delta_t) for p in range(process_count)}

    
    suspended = {p: False for p in range(process_count)}
    available_frames = 0
    current_ppf = {p: 0.0 for p in range(process_count)}
    current_time = 0
    log_data = []
    frame_actions = {p: None for p in range(process_count)}
    #-----------------------------------------------------------------------------------------------
    

    #SECOND_CHANCE
    #-----------------------------------------------------------------------------------------------
    for idx, (process_id, page, time, _) in enumerate(sorted(ciag_odwolan, key=lambda x: x[2])):
        #JEŻELI PROCES PROCES WSTRZYMANY
        if suspended[process_id]:
            page_fault_occurred = False
        #JEŻELI DALEJ DZIAŁĄ
        else:
            #POBIERAM JEGO STRONY
            pamiec = pamiec_procesow[process_id]
            bity = bity_procesow[process_id]
            frame_limit = process_frame_counts[process_id]


            #JEŻELI BŁĄD SIĘ NIE POJAWIA
            if page in bity:
                bity[page] = 1
                page_fault_occurred = False
                recent_faults[process_id].append(0)

            #JEŻELI BŁĄD SIĘ POJAWIA
            else:
                # Błąd strony
                bledy_procesow[process_id] += 1
                recent_faults[process_id].append(1)
                page_fault_occurred = True

                if len(pamiec) < frame_limit:
                    pamiec.append(page)
                    bity[page] = 1
                else:
                    # Second Chance - szukamy strony do usunięcia
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
    #-----------------------------------------------------------------------------------------------

        # Aktualizacja PPF i przydział ramek co delta_t odwołań
        if (idx + 1) % delta_t == 0 and idx > 0:
                    #USTALANIE CZASU
                    current_time += delta_t
                    frame_actions = {p: None for p in range(process_count)}  # resetujemy akcje

                    #DLA KAŻDEGO PROCESU
                    for pid in range(process_count):
                        if suspended[pid]: #JEŻELI JEST JUŻ ZATRZYMANY
                            current_ppf[pid] = -1
                        else: #JEŻELI PROCES NIE JEST JESZCZE ZATRZYMANY
                            faults = sum(recent_faults[pid])
                            current_ppf[pid] = faults / delta_t

                            # JEŻELI PPF WIĘKSZE OD MAKSYMALNEGO OGRANICZENIA
                            if  current_ppf[pid] > high_threshold:  
                                suspended[pid] = True
                                available_frames += process_frame_counts[pid]
                                process_frame_counts[pid] = 0
                                frame_actions[pid] = "suspended"

                            # JEŻELI PPF WIĘKSZE OD ŚREDNIEGO OGRANICZENIA ALE NIE MA WOLNYCH RAMEK
                            elif current_ppf[pid] > upper_threshold and available_frames==0:
                                suspended[pid] = True
                                available_frames += process_frame_counts[pid]
                                process_frame_counts[pid] = 0
                                frame_actions[pid] = "suspended"

                            #JEŻELI WYŻSZE, ALE SĄ WOLNE RAMKI 
                            elif current_ppf[pid] > upper_threshold:
                                if available_frames > 0:
                                    process_frame_counts[pid] += 1
                                    available_frames -= 1
                                    frame_actions[pid] = "gained"

                            #JEŻELI NIŻSZE OD DOLNEGO OGRANICZENIA
                            elif current_ppf[pid] < lower_threshold:
                                if process_frame_counts[pid] > 1:
                                    process_frame_counts[pid] -= 1
                                    available_frames += 1
                                    if pamiec_procesow[pid]:
                                        to_remove = random.choice(list(pamiec_procesow[pid]))
                                        pamiec_procesow[pid].remove(to_remove)
                                        del bity_procesow[pid][to_remove]
                                    frame_actions[pid] = "lost"

                    # Logowanie rzeczywistych stanów procesów
                    for pid in range(process_count):
                        log_data.append({
                            'timestamp': current_time,
                            'process_id': pid,
                            'current_ppf': current_ppf[pid],
                            'allocated_frames': process_frame_counts[pid],
                            'page_fault_occurred': page_fault_occurred if pid == process_id else None,
                            'process_suspended': suspended[pid],
                            'frame_action': frame_actions[pid]
                        })

    return bledy_procesow, suspended, log_data 