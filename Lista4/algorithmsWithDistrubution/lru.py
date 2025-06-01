def lru_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions):
    """
    ciag_odwolan: lista krotek (process_id, page, czas, faza)
    total_frames: całkowita liczba dostępnych ramek
    process_count: liczba procesów
    process_proportions: lista proporcji
    """

    # 1. Przydział pamięci dla każdego procesu
    #-----------------------------------------------------------------------------------------------
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)  # korekta
    #-----------------------------------------------------------------------------------------------

    # 2. Inicjalizacja pamięci i liczników błędów dla każdego procesu
    #-----------------------------------------------------------------------------------------------
    pamiec_procesow = {p: {} for p in range(process_count)}  # {strona: czas_od_uzycia}
    bledy_procesow = {p: 0 for p in range(process_count)}
    #-----------------------------------------------------------------------------------------------

    # 3. Przetwarzanie żądań
    #-----------------------------------------------------------------------------------------------
    for process_id, page, _, _ in sorted(ciag_odwolan, key=lambda x: x[2]):
        pamiec = pamiec_procesow[process_id]
        rozmiar_pamieci = process_frame_counts[process_id]

        # Zwiększ czas od ostatniego użycia dla każdej strony
        for s in pamiec:
            pamiec[s] += 1

        if page in pamiec:
            pamiec[page] = 0  # użyta strona — reset czasu
        else:
            bledy_procesow[process_id] += 1

            if len(pamiec) < rozmiar_pamieci:
                pamiec[page] = 0
            else:
                # usuń stronę najdłużej nieużywaną (największy czas)
                do_usuniecia = max(pamiec.items(), key=lambda x: x[1])[0]
                del pamiec[do_usuniecia]
                pamiec[page] = 0

        pamiec_procesow[process_id] = pamiec
    #-----------------------------------------------------------------------------------------------

    return bledy_procesow
