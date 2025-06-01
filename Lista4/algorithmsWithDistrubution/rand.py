import random

def rand_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions):
    """
    ciag_odwolan: lista krotek (process_id, page, czas, faza)
    total_frames: całkowita liczba dostępnych ramek
    process_count: liczba procesów
    process_proportions: lista proporcji (np. [0.25, 0.25, 0.25, 0.25])
    """

    # 1. Przydział ramek dla każdego procesu
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)  # korekta

    # 2. Inicjalizacja struktur
    pamiec_procesow = {p: set() for p in range(process_count)}
    bledy_procesow = {p: 0 for p in range(process_count)}

    # 3. Przetwarzanie żądań
    for process_id, page, _, _ in sorted(ciag_odwolan, key=lambda x: x[2]):
        pamiec = pamiec_procesow[process_id]
        rozmiar_pamieci = process_frame_counts[process_id]

        if page in pamiec:
            continue  # brak błędu

        # Błąd strony
        bledy_procesow[process_id] += 1

        if len(pamiec) < rozmiar_pamieci:
            pamiec.add(page)
        else:
            # Usuwamy losową stronę z pamięci danego procesu
            strona_do_usuniecia = random.choice(list(pamiec))
            pamiec.remove(strona_do_usuniecia)
            pamiec.add(page)

        pamiec_procesow[process_id] = pamiec

    return bledy_procesow
