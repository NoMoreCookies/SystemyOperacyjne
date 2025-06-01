from collections import defaultdict

def fifo_procesowy(ciag_odwolan,virtual_capacity, process_count, process_proportions):
    """
    ciag_odwolan: lista krotek (process_id, page, czas, faza)
    total_frames: całkowita liczba dostępnych ramek
    process_count: liczba procesów
    process_proportions: lista proporcji (np. [0.25, 0.25, 0.25, 0.25])
    """

    # 1. Przydział pamięci dla każdego procesu
    #-----------------------------------------------------------------------------------------------
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    # Korekta sumy (dla błędów zaokrągleń)
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)
    #-----------------------------------------------------------------------------------------------

    # 2. Inicjalizacja pamięci i liczników błędów dla każdego procesu
    #-----------------------------------------------------------------------------------------------
    pamiec_procesow = {p: [] for p in range(process_count)}  # pamiec procesów: {pid: [(page, age), ...]}
    bledy_procesow = {p: 0 for p in range(process_count)}
    #-----------------------------------------------------------------------------------------------

    # 3. Przetwarzanie każdego żądania
    #-----------------------------------------------------------------------------------------------
    for process_id, page, _, _ in sorted(ciag_odwolan, key=lambda x: x[2]):
        pamiec = pamiec_procesow[process_id]
        rozmiar_pamieci = process_frame_counts[process_id]
    #-----------------------------------------------------------------------------------------------

        # Zwiększ wiek stron
        #-----------------------------------------------------------------------------------------------
        pamiec = [(s, wiek + 1) for s, wiek in pamiec]
        #-----------------------------------------------------------------------------------------------


        # Sprawdź, czy strona jest już w pamięci
        #-----------------------------------------------------------------------------------------------
        if any(s == page for s, _ in pamiec):
            pamiec_procesow[process_id] = pamiec  # aktualizuj wieki
            continue
        #-----------------------------------------------------------------------------------------------

        # Błąd strony
        #-----------------------------------------------------------------------------------------------
        bledy_procesow[process_id] += 1
        #-----------------------------------------------------------------------------------------------

        # Dodaj nową stronę lub usuń najstarszą
        #-----------------------------------------------------------------------------------------------
        if len(pamiec) < rozmiar_pamieci:
            pamiec.append((page, 0))
        else:
            # FIFO – usuń stronę o największym wieku
            do_usuniecia = max(pamiec, key=lambda x: x[1])
            pamiec.remove(do_usuniecia)
            pamiec.append((page, 0))

        pamiec_procesow[process_id] = pamiec
        print(pamiec)
        #-----------------------------------------------------------------------------------------------

    return bledy_procesow
