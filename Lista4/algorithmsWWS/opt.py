from collections import deque

def opt_wws_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                      delta_t=10, c_factor=0.3):
    
    #INICJALIZACJA ZMIENNYCH POMOCNICZYCH
    #-----------------------------------------------------------------------------------------------
    # Proporcjonalny początkowy podział ramek
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)

    odwolania_per_process = {p: [] for p in range(process_count)}
    for r in sorted(ciag_odwolan, key=lambda x: x[2]):
        odwolania_per_process[r[0]].append(r)

    pamiec_procesow = {p: [] for p in range(process_count)}
    bledy_procesow = {p: 0 for p in range(process_count)}
    suspended = {p: False for p in range(process_count)}
    indices = {p: 0 for p in range(process_count)}
    recent_pages = {p: deque(maxlen=delta_t) for p in range(process_count)}
    log_data = []
    current_time = 0

    total_requests_sorted = sorted(ciag_odwolan, key=lambda x: x[2])
    c = int(c_factor * delta_t)
    #-----------------------------------------------------------------------------------------------
    for idx, (process_id, page, time, _) in enumerate(total_requests_sorted):
        if suspended[process_id]:
            page_fault_occurred = False

        else:

            pamiec = pamiec_procesow[process_id]
            ramki = process_frame_counts[process_id]

            #JEŻELI WYSTĄPIŁ BŁĄD
            if page not in pamiec:

                bledy_procesow[process_id] += 1
                page_fault_occurred = True

                if len(pamiec) < ramki:
                    pamiec.append(page)
                elif ramki > 0:
                    # ALGORYTM OPT
                    odwolania = odwolania_per_process[process_id]
                    current_index = indices[process_id]
                    przyszle = [odw[1] for odw in odwolania[current_index + 1:]]
                    indeksy = [przyszle.index(s) if s in przyszle else float('inf') for s in pamiec]
                    do_usuniecia = indeksy.index(max(indeksy))
                    pamiec[do_usuniecia] = page
                # else: brak ramek, ale nie robimy nic
            else:
                page_fault_occurred = False
                bledy_procesow[process_id] += 0

            pamiec_procesow[process_id] = pamiec

        recent_pages[process_id].append(page if not suspended[process_id] else None)
        indices[process_id] += 1
    #-----------------------------------------------------------------------------------------------

        # Aktualizacja co c wywołań (nie co delta_t)
        if (idx + 1) % c == 0:
            current_time += c
            wss_sizes = {}
            for pid in range(process_count):
                wss_sizes[pid] = len(set(p for p in recent_pages[pid] if p is not None))

            total_wss = sum(wss_sizes[pid] for pid in range(process_count) if not suspended[pid])

            # Wstrzymywanie jeśli D > dostępna pamięć
            available_frames = virtual_capacity
            if total_wss > virtual_capacity:
                active = [pid for pid in range(process_count) if not suspended[pid]]
                sorted_by_wss = sorted(active, key=lambda p: wss_sizes[p], reverse=True)
                for pid in sorted_by_wss:
                    if total_wss <= virtual_capacity:
                        break
                    suspended[pid] = True
                    total_wss -= wss_sizes[pid]
                    process_frame_counts[pid] = 0
                    pamiec_procesow[pid].clear()
                    recent_pages[pid].clear()

            # Aktualny podział ramek proporcjonalnie do WSS
            active = [pid for pid in range(process_count) if not suspended[pid]]
            total_wss = sum(wss_sizes[pid] for pid in active)
            for pid in active:
                if total_wss > 0:
                    przydzial = int(wss_sizes[pid] / total_wss * virtual_capacity)
                else:
                    przydzial = 1
                process_frame_counts[pid] = przydzial
                available_frames -= przydzial

            # Korekta — dodaj brakujące ramki największemu WSS
            diff = available_frames
            if diff != 0 and active:
                max_pid = max(active, key=lambda p: wss_sizes[p])
                process_frame_counts[max_pid] += diff

            # Wznawianie procesów
            for pid in range(process_count):
                if suspended[pid]:
                    req = wss_sizes[pid]
                    if req <= available_frames:
                        suspended[pid] = False
                        process_frame_counts[pid] = req
                        available_frames -= req

                        # Przywróć pamięć procesu na podstawie ostatnich unikalnych odwołań
                        pamiec_procesow[pid].clear()
                        unique_pages = []
                        seen = set()
                        # Od najnowszych do najstarszych stron
                        for page in reversed(recent_pages[pid]):
                            if page is not None and page not in seen:
                                unique_pages.append(page)
                                seen.add(page)
                            if len(unique_pages) >= req:
                                break
                        unique_pages.reverse()

                        # Wypełnij pamiec_procesow zgodnie z unikalnymi stronami
                        pamiec_procesow[pid].extend(unique_pages)

            # Logowanie
            for pid in range(process_count):
                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_wss_size': wss_sizes[pid],
                    'allocated_frames': process_frame_counts[pid],
                    'page_fault_occurred': page_fault_occurred if pid == process_id else None,
                    'process_suspended': suspended[pid]
                })

    return bledy_procesow, suspended, log_data
