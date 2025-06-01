from collections import deque

def fifo_wws_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                                      delta_t=10, c_factor=0.3):

    #INICJALIZACJA_POMOCNICZYCH_ZMIENNYCH
    #-----------------------------------------------------------------------------------------------

    #LICZNIK CZASU ORAZ PAMIEĆ FIZYCZNA
    total_frames = virtual_capacity
    current_time = 0

    # Przydział początkowy ramek proporcjonalnie do process_proportions
    process_frame_counts = [int(total_frames * p) for p in process_proportions]

    # Korekta, by suma ramek równała się total_frames (NAPRAWA BŁĘDÓW NUMERYCZNYCH)
    process_frame_counts[0] += total_frames - sum(process_frame_counts)

    # RAMKI PAMIĘCI DLA DANEGO PROCESU
    pamiec_procesow = {p: deque() for p in range(process_count)}

    # LICZNIK BŁĘDÓW DLA KAŻDEGO PROCESU
    bledy_procesow = {p: 0 for p in range(process_count)}

    # HISTORIA OSTATNICH ODWOŁAŃ DO STRON
    access_history = {p: deque(maxlen=delta_t) for p in range(process_count)}
    suspended = {p: False for p in range(process_count)}
    log_data = []
    
    # C
    c = int(c_factor * delta_t)
    #-----------------------------------------------------------------------------------------------

    #ZBIERANIE DANYCH
    #-----------------------------------------------------------------------------------------------

    # DLA KAŻDEGO REQUESTA BIERZEMY JE, SORTUJĄC PO CZASIE
    for idx, (process_id, page, time, _) in enumerate(sorted(ciag_odwolan, key=lambda x: x[2])):
        
        # JEŻELI PROCES JEST JUŻ ZATRZYMANY TO GO SKIPUJEMY
        if suspended[process_id]:
            page_fault_occurred = False
        #JEŻELI NIE JEST ZATRZYMANY TO DODAJEMY STRONE KTÓRĄ WYWOŁAŁ DO HISTORI
        else: 
            #POBIERAMY RAMKI PROCESU ORAZ ICH LIMIT
            access_history[process_id].append(page)
            memory = pamiec_procesow[process_id]
            frame_limit = process_frame_counts[process_id]

            #JEŻELI STRONA JEST JUŻ W RAMKACH TO BŁĄD SIĘ NIE POJAWIŁ
            if page in memory:
                page_fault_occurred = False
            #JEŻELI STRONY NIE MA W RAMKACH
            else:
                page_fault_occurred = True
                bledy_procesow[process_id] += 1

                if len(memory) < frame_limit:
                    memory.append(page)
                else:
                    if frame_limit > 0: #TUTAJ TROCHĘ NW CZEMU ALE CZASAMI POJAWIA MI SIĘ Z TYM BŁĄD, WIĘC NOM....IDQ
                        memory.popleft()
                    memory.append(page)
        #----------------------------------------------------------------------------------------------- Wygląda poprawnie

        #OBSŁUGA WWS
        #---------------------------------------------------------------------------------------------
        if (idx + 1) % c == 0:

            current_time += c
            current_wss = {}

            for pid in range(process_count):
                if not suspended[pid]:
                    current_wss[pid] = len(set(access_history[pid]))
                else:
                    current_wss[pid] = 0  # wstrzymany proces ma WSS=0

            sum_wss = sum(current_wss.values())
            active_processes = [pid for pid in range(process_count) if not suspended[pid]]

            # Wstrzymywanie procesów, aż suma WSS aktywnych procesów zmieści się w ramkach
            while sum_wss > total_frames and active_processes:
                # Strategia: zatrzymujemy proces o największym WSS
                victim = max(active_processes, key=lambda p: current_wss[p])
                suspended[victim] = True
                process_frame_counts[victim] = 0
                pamiec_procesow[victim].clear()

                current_wss[victim] = 0
                active_processes.remove(victim)
                sum_wss = sum(current_wss[pid] for pid in active_processes)

            # Teraz proporcjonalny podział ramek na podstawie WSS i podanych proporcji

           # Teraz proporcjonalny podział ramek na podstawie WSS i podanych proporcji
            if sum_wss > 0:
                wss_ratios = {pid: current_wss[pid]/sum_wss for pid in active_processes}
                for pid in range(process_count):
                    if pid in active_processes:
                        allocated = int(wss_ratios[pid] * total_frames)
                        process_frame_counts[pid] = max(allocated, 1)
                    else:
                        process_frame_counts[pid] = 0
            else:
                for pid in range(process_count):
                    process_frame_counts[pid] = 0

            # -------------------------- WZNAWIANIE PROCESÓW --------------------------
            used_frames = sum(process_frame_counts[pid] for pid in range(process_count))
            free_frames = total_frames - used_frames

            # SPRAWDZAMY CZY MOŻNA WZNOWIĆ JAKIŚ WSTRZYMANY PROCES
            for pid in range(process_count):
                if suspended[pid]:
                    estimated_wss = len(set(access_history[pid]))
                    if estimated_wss <= free_frames and estimated_wss > 0:
                        suspended[pid] = False
                        process_frame_counts[pid] = estimated_wss
                        # PRZYWRACAMY STAN PAMIĘCI - DODAJEMY OSTATNIE STRONY Z HISTORII
                        pamiec_procesow[pid].clear()
                        seen = set()
                        for page in reversed(access_history[pid]):
                            if page not in seen:
                                pamiec_procesow[pid].appendleft(page)
                                seen.add(page)
                            if len(pamiec_procesow[pid]) >= estimated_wss:
                                break
                        free_frames -= estimated_wss
            # -------------------------------------------------------------------------
            # Logowanie danych
            for pid in range(process_count):
                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_wss': current_wss[pid],
                    'allocated_frames': process_frame_counts[pid],
                    'page_fault_occurred': page_fault_occurred if process_id == pid else None,
                    'process_suspended': suspended[pid],
                })

    return bledy_procesow, suspended, log_data
