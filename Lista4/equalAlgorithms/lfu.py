from collections import deque

def second_chance_procesowy1(ciag_odwolan, virtual_capacity, process_count, process_proportions):
    """
    ciag_odwolan: lista krotek (process_id, page, czas, faza)
    total_frames: całkowita liczba dostępnych ramek
    process_count: liczba procesów
    process_proportions: lista proporcji
    """

    # 1. Przydział pamięci dla każdego procesu
    #-----------------------------------------------------------------------------------------------
    process_frame_counts = [int(virtual_capacity * 1/len(process_proportions)) for p in process_proportions]
    # Korekta sumy dla błędów zaokrągleń
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)
    #-----------------------------------------------------------------------------------------------

    # 2. Inicjalizacja struktur dla każdego procesu
    #-----------------------------------------------------------------------------------------------
    pamiec_procesow = {p: deque() for p in range(process_count)}
    bity_procesow = {p: {} for p in range(process_count)}
    bledy_procesow = {p: 0 for p in range(process_count)}
    #-----------------------------------------------------------------------------------------------

    # 3. Przetwarzanie żądań w kolejności czasowej
    #-----------------------------------------------------------------------------------------------
    for process_id, page, _, _ in sorted(ciag_odwolan, key=lambda x: x[2]):
        pamiec = pamiec_procesow[process_id]
        bity = bity_procesow[process_id]
        rozmiar_pamieci = process_frame_counts[process_id]

        # Sprawdzenie, czy strona jest w pamięci
        if page in bity:
            bity[page] = 1  # ustawiamy bit odwołania
            continue  # brak błędu

        # Błąd strony
        bledy_procesow[process_id] += 1

        if len(pamiec) < rozmiar_pamieci:
            # Jest miejsce – dodaj nową stronę
            pamiec.append(page)
            bity[page] = 1
        else:
            # Szukamy strony do usunięcia zgodnie z Second Chance
            while True:
                oldest = pamiec[0]
                if bity[oldest] == 0:
                    # Usuń stronę bez bitu
                    pamiec.popleft()
                    del bity[oldest]
                    break
                else:
                    # Daj drugą szansę
                    pamiec.popleft()
                    pamiec.append(oldest)
                    bity[oldest] = 0

            # Dodaj nową stronę
            pamiec.append(page)
            bity[page] = 1

        # Zapisz zaktualizowane struktury
        pamiec_procesow[process_id] = pamiec
        bity_procesow[process_id] = bity
    #-----------------------------------------------------------------------------------------------

    return bledy_procesow
