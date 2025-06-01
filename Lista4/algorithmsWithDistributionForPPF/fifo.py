import random
from collections import deque

def fifo_ppf_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                       delta_t=100, lower_threshold=0.1, upper_threshold=0.25, high_threshold=0.5):
    
    #PRZYPISUJĘ PROPORCJONALNĄ ILOŚĆ RAMEK FIZYCZNYCH DO KAŻDEGO PROCESU ZGODNIE Z PODANYMI PROPORCJAMI
    #-----------------------------------------------------------------------------------------------
    current_time = 0 
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)
    print(process_frame_counts)
    #-----------------------------------------------------------------------------------------------

    #TUTAJ DLA KAŻDEGO PROCESU JEST PRZECHOWYWANA LICZBA STRON, KTÓRA AKTUALNEI MIEŚCI SIĘ W JEGO RAMKACH
    #-----------------------------------------------------------------------------------------------
    pamiec_procesow = {p: deque() for p in range(process_count)}
    bledy_procesow = {p: 0 for p in range(process_count)}
    #-----------------------------------------------------------------------------------------------
    
    #OGL TUTAJ DLA KAŻDEGO PROCESU PRZECHOWUJEMY LICZBĘ BŁĘDÓW W OSTATNICH DELTA T ZAPYTANIACH
    #-----------------------------------------------------------------------------------------------
    recent_faults = {p: deque(maxlen=delta_t) for p in range(process_count)}
    #-----------------------------------------------------------------------------------------------

    #PROSTA TABLICA INFORMUJĄCA CZY DANY PROCES JEST OBECNIE ZATRZYMANY CZY NIE
    #-----------------------------------------------------------------------------------------------
    suspended = {p: False for p in range(process_count)}
    available_frames = 0
    log_data = []
    current_ppf = {p: 0.0 for p in range(process_count)}
    #-----------------------------------------------------------------------------------------------

    #FIFO
    #-----------------------------------------------------------------------------------------------
    for idx, (process_id, page, time, _) in enumerate(sorted(ciag_odwolan, key=lambda x: x[2])):
        #JEŻELI ZATRZYMANY TO IDĘ DALEJ, NIC SIĘ NIE ZMIENIA
        
        if suspended[process_id]: # JEŻELI PROCES JEST JUŻ ZATRZYMANY
            page_fault_occurred = False
        else: # JEŻELI PROCES NIE JEST ZATRZYMANY
            
            #Pobieram pamięc danegoi procesu
            memory = pamiec_procesow[process_id]

            #Pobieram jaki ten proces ma frame limit obecny
            frame_limit = process_frame_counts[process_id]

            
            if page in memory: # JEŻELI POSIADAMY DANĄ STRONĘ W PAMIĘCI NASZEGO PROCESU

                # Trafienie (strona już jest w pamięci)
                page_fault_occurred = False
                recent_faults[process_id].append(0)  # brak błędu

            else: # JEŻELI WYSTĘPUJĘ BŁĄD
                # Brak strony w pamięci — błąd strony (page fault)
                page_fault_occurred = True

                #DODAJEMY BŁĄD
                bledy_procesow[process_id] += 1
                recent_faults[process_id].append(1)  
                
                #JEŻELI JEST WOLNE MIEJSCE W PAMIECI TO WSTAWIAMY PO PROSTU TAM STRONĘ
                if len(memory) < frame_limit  :
                    memory.append(page)
                else: #JEŻELI NIE MA TO UŻYWAMY FIFA
                    if(memory):
                        memory.popleft()
                    memory.append(page)

        
        #TERAZ LICZĘ WSPÓŁCZYNNIK PPF ORAZ MODYFIKUJĘ RAMKI
        #-----------------------------------------------------------------------------------------------
        if (idx+1) % delta_t == 0 :
        
            # LICZĘ CZAS W JAKIM SPRAWCZAM PPF
            current_time+=delta_t

            # TERAZ W DANEJ CHWILI DLA KAŻDEGO PROCESU OBLICZAM PPF
            for pid in range(process_count):

                if suspended[pid]:#JEŻELI ZATRZYMANY TO PPF DLA REPREZENTACJI
                    current_ppf[pid] = -1 
                else: #JEŻELI NIE JEST SUSPENDED
                    faults = sum(recent_faults[pid])
                    current_ppf[pid] = faults / delta_t 

                    # JEŚLI WIĘKSZE OD HIGH_THRESHOLD TO ZATRZYMUJE
                    if current_ppf[pid] > high_threshold:
                        suspended[pid] = True
                        available_frames += process_frame_counts[pid]
                        process_frame_counts[pid] = 0


                    #JEŚLI WIĘKSZE OD UPPER  I NIE MA MIEJSC TO ZATRZYMUJĘ
                    elif current_ppf[pid] > upper_threshold and available_frames==0:
                        # PPF przekroczył h — zawieszamy proces niezależnie od dostępnych ramek
                        suspended[pid] = True
                        available_frames += process_frame_counts[pid]
                        process_frame_counts[pid] = 0

                    # JEŻLI WIĘKSZE OD UPPER DO DODAJĘ RAMKE
                    elif current_ppf[pid] > upper_threshold:
                        if available_frames > 0:
                            process_frame_counts[pid] += 1
                            available_frames -= 1
                    # JEŚLI MNIEJSZE OD DOLNEGO PROGU TO ZABIERAM RAMKĘ
                    elif current_ppf[pid] < lower_threshold:
                        if process_frame_counts[pid] > 0:  # <-- TU
                            process_frame_counts[pid] -= 1
                            available_frames += 1
                            if pamiec_procesow[pid]:
                                remove_idx = random.randint(0, len(pamiec_procesow[pid]) - 1)
                                del pamiec_procesow[pid][remove_idx]
            #-----------------------------------------------------------------------------------------------

            # ZAPISYWANIE STANÓW PROCESÓW W DANEJ CHWILI
            #-----------------------------------------------------------------------------------------------
            for pid in range(process_count):
                if suspended[pid] :
                    action = "suspended"
                elif current_ppf[pid] > upper_threshold  :
                    action = "gained"
                elif current_ppf[pid] < lower_threshold :
                    action = "lost"
                else:
                    action = None

                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_ppf': current_ppf[pid],
                    'allocated_frames': process_frame_counts[pid],
                    'page_fault_occurred': page_fault_occurred if process_id == pid else None,
                    'process_suspended': suspended[pid],
                    'frame_action': action
                })
            #-----------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------

    return bledy_procesow, suspended, log_data
