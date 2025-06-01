from collections import deque
import random

def second_chance_wws_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                                delta_t=10, c_factor=0.3):
    #INICJALIZACJA ZMIENNYCH POMOCNICZYCH
    #-----------------------------------------------------------------------------------------------

    #OBECNY CZAS I PAMIĘĆ FIZYCZNA
    current_time = 0
    total_frames = virtual_capacity

    # Inicjalizacja ramek według proporcji (zaokrąglone i wyrównanie)
    process_frame_counts = [int(total_frames * p) for p in process_proportions]

    # Korekta ewentualnej różnicy przy zaokrągleniach (przydziel nadmiar do procesu 0)
    process_frame_counts[0] += total_frames - sum(process_frame_counts)

    #POCZĄTKOWE RAMKI DO KAŻDEGO PROCESU
    pamiec_procesow = {p: deque() for p in range(process_count)}

    #SECOND CHANCE WIĘC JESZCZE KOLEJKA KIEDY DANY PROCES OSTATNIO UŻYWAŁ DANEJ RAMKI
    bity_procesow = {p: {} for p in range(process_count)}

    #BŁĘDY DLA KAŻDEGO PROCESU, ŻEBY POTEM JE ZSUMOWAĆ
    bledy_procesow = {p: 0 for p in range(process_count)}

    #DO ALGORYTMU WWS, SPRAWDZANIE KIEDY DANY PROCES OSTATNI RAZ UŻYWAŁ DANEJ RAMKI
    access_history = {p: deque(maxlen=delta_t) for p in range(process_count)}

    #CZY PROCES JEST WSTRZYMANY
    suspended = {p: False for p in range(process_count)}

    #HISTORIA OPERACJI PROCESÓW
    log_data = []

    #INICJALIZACJA DELTA_T
    c = int(c_factor * delta_t)
    #-----------------------------------------------------------------------------------------------

    # ALGORYTM SECOND CHANCE
    #-----------------------------------------------------------------------------------------------
    for idx, (process_id, page, time, _) in enumerate(sorted(ciag_odwolan, key=lambda x: x[2])):

        #JEŻELI ZATRZYAMNY TO SKIP 
        if  suspended[process_id]:
                bledy_procesow[process_id]+=0
        # JEŻELI NIE ZATRZYMANY TO :
        else:
            access_history[process_id].append(page)
            pamiec = pamiec_procesow[process_id]
            bity = bity_procesow[process_id]
            frame_limit = process_frame_counts[process_id]

            # STRONA W PAMIĘCI
            if page in bity:
                bity[page] = 1
            else:
                # BŁĄD STRONY
                bledy_procesow[process_id] += 1

                if len(pamiec) < frame_limit:
                    pamiec.append(page)
                    bity[page] = 1
                else:
                    #NOI TUTAJ IMPLEMENTACJA SECOND_CHANCE
                    while True:
                        if not pamiec:  # jeśli pamiec jest pusta, przerwij pętlę (bez sensu kontynuować)
                            break
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

            pamiec_procesow[process_id] = pamiec
            bity_procesow[process_id] = bity
    #-----------------------------------------------------------------------------------------------

        # AKTUALIZACJA CO c
        if (idx + 1) % c == 0:
            current_time += c
            current_wss = {}
            for pid in range(process_count):
                if not suspended[pid]:
                    current_wss[pid] = len(set(access_history[pid]))
                else:
                    current_wss[pid] = 0

            total_wss = sum(current_wss.values())

            # Jeśli WSS przekracza dostępne ramki - wstrzymanie procesów
            while total_wss > total_frames:
                active = [pid for pid in range(process_count) if not suspended[pid]]
                if not active:
                    break
                victim = max(active, key=lambda p: current_wss[p])
                suspended[victim] = True
                total_wss -= current_wss[victim]
                total_frames += process_frame_counts[victim]  # zwolnij ramki
                process_frame_counts[victim] = 0
                pamiec_procesow[victim].clear()
                bity_procesow[victim].clear()

            # Proporcjonalny podział ramek na podstawie WSS
            active_processes = [pid for pid in range(process_count) if not suspended[pid]]
            available_frames = total_frames - sum(process_frame_counts[pid] for pid in active_processes)
            active_processes = [pid for pid in range(process_count) if not suspended[pid]]
            if active_processes and total_wss > 0:
                for pid in active_processes:
                    proportion = current_wss[pid] / total_wss
                    allocated = int(proportion * total_frames)
                    process_frame_counts[pid] = allocated
                    available_frames -= allocated

                # Dopasuj różnicę (jeśli jakaś została) do procesu o największym WSS
                diff = available_frames
                if diff != 0:
                    max_pid = max(active_processes, key=lambda p: current_wss[p])
                    process_frame_counts[max_pid] += diff
            else:
                # Jeśli brak aktywnych procesów lub total_wss=0, rozdziel ramki równo lub zostaw puste
                pass

            # WZNOWIENIE PROCESÓW
            for pid in range(process_count):
                if suspended[pid]:
                    required = len(set(access_history[pid]))
                    if required <= available_frames:
                        suspended[pid] = False
                        process_frame_counts[pid] = required
                        available_frames -= required

                        # Przywracamy zawartość pamięci i bity procesu z historii odwołań
                        pamiec_procesow[pid].clear()
                        bity_procesow[pid].clear()
                        seen_pages = set()
                        # Iterujemy od końca, żeby brać ostatnie unikalne strony
                        for page in reversed(access_history[pid]):
                            if page not in seen_pages:
                                pamiec_procesow[pid].appendleft(page)
                                bity_procesow[pid][page] = 1  # ustawiamy bit na 1, bo była ostatnio używana
                                seen_pages.add(page)
                            if len(pamiec_procesow[pid]) >= required:
                                break

            # LOGOWANIE
            for pid in range(process_count):
                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_wss': current_wss[pid],
                    'allocated_frames': process_frame_counts[pid],
                    'process_suspended': suspended[pid]
                })

    return bledy_procesow, suspended, log_data
