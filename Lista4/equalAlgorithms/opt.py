def opt_procesowy1(ciag_odwolan, virtual_capacity, process_count, process_proportions):
    """
    ciag_odwolan: lista krotek (process_id, page, czas, faza)
    total_frames: całkowita liczba dostępnych ramek
    process_count: liczba procesów
    process_proportions: lista proporcji (np. [0.25, 0.25, 0.25, 0.25])
    """

    # 1. Przydział pamięci dla każdego procesu
    #-----------------------------------------------------------------------------------------------
    process_frame_counts = [int(virtual_capacity * 1/len(process_proportions)) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)  # korekta
    #-----------------------------------------------------------------------------------------------

    # 2. Wyodrębnij żądania per proces
    #-----------------------------------------------------------------------------------------------
    odwolania_per_process = {p: [] for p in range(process_count)}
    for r in sorted(ciag_odwolan, key=lambda x: x[2]):
        odwolania_per_process[r[0]].append(r)
    #-----------------------------------------------------------------------------------------------

    # 3. Inicjalizacja
    #-----------------------------------------------------------------------------------------------
    pamiec_procesow = {p: [] for p in range(process_count)}
    bledy_procesow = {p: 0 for p in range(process_count)}
    #-----------------------------------------------------------------------------------------------

    # 4. Przetwarzanie dla każdego procesu osobno
    #-----------------------------------------------------------------------------------------------
    for pid in range(process_count):
        pamiec = pamiec_procesow[pid]
        rozmiar_pamieci = process_frame_counts[pid]
        odwolania = odwolania_per_process[pid]

        for i, (_, page, _, _) in enumerate(odwolania):
            if page in pamiec:
                continue

            bledy_procesow[pid] += 1

            if len(pamiec) < rozmiar_pamieci:
                pamiec.append(page)
            else:
                przyszle = [odw[1] for odw in odwolania[i+1:]]  # przyszłe strony
                indeksy = []
                for s in pamiec:
                    try:
                        indeksy.append(przyszle.index(s))
                    except ValueError:
                        indeksy.append(float('inf'))  # nie pojawi się więcej

                # znajdź stronę najpóźniej używaną w przyszłości
                index_do_usuniecia = indeksy.index(max(indeksy))
                pamiec[index_do_usuniecia] = page

        pamiec_procesow[pid] = pamiec
    #-----------------------------------------------------------------------------------------------

    return bledy_procesow
