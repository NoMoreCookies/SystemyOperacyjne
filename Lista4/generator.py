import random
from collections import defaultdict
#FUNKCJA GENERUJĄCA REQUESTY
#-----------------------------------------------------------------------------------------------
def generate_requests(process_count, total_frames, total_requests, phases, process_proportions):
    """
    process_count: liczba procesów
    total_frames: łączna liczba ramek (stron)
    total_requests: liczba requestów (odwołań)
    phases: liczba faz
    process_proportions: lista udziałów każdego procesu (sumuje się do 1)TUTAJ MUSZĘ TO JESZCZE ZMIENIĆ,ONA MÓWI O TYM ILE ZAJMUJĄ WSZYSTKICH RAMEK,
    ALE NIE MÓWI O TYM JAK SĄ GENEROWANE,GENEROWANE POWINNY CHYBA ZOSTAĆ LOSOWO, I GUESS, ALE IMO TO CO ZROBIŁEM NIE JEST ZŁE
    """
    # 1. Przydziel każdemu procesowi unikalny zestaw stron (ramki) PROPORCJONALNIE DO Udziałów
    #------------------------------------------------------------------------------------------

    # Tworzy listę wszystkich indeksów klatek od 0 do total_frames - 1
    all_frames = list(range(total_frames))

    # Losowo miesza kolejność klatek, aby były rozdzielane w sposób losowy
    random.shuffle(all_frames)

    # Oblicza liczbę klatek przypadających na każdy proces, na podstawie proporcji (process_proportions)
    frame_counts = [int(total_frames * p) for p in process_proportions]

    # Korekta, aby suma frame_counts dokładnie wynosiła total_frames (ze względu na zaokrąglenia,błedy numeryczne)
    frame_counts[0] += total_frames - sum(frame_counts)

    # Tworzy słownik, który przypisuje procesom odpowiednie klatki(to potem się przydaje w wypisywaniu)
    process_frames = {}
    idx = 0
    for i, count in enumerate(frame_counts):
        # Dla każdego procesu (i), przypisuję `count` klatek z all_frames, zaczynając od indeksu idx
        process_frames[i] = all_frames[idx:idx + count]
        # Zaktualizuj indeks do początku kolejnego zakresu
        idx += count
        
    #------------------------------------------------------------------------------------------

    # 2. Losowy podział stron każdego procesu na fazy (PODZIAŁ PROCESÓW NA FAZY)
    #------------------------------------------------------------------------------------------
    # Tworzy słownik, który będzie zawierał klatki przypisane do każdej fazy dla każdego procesu
    process_phase_frames = {}

    # Iteruje przez wszystkie procesy
    for p in range(process_count):

        # Tworzy kopię listy klatek przypisanych danemu procesowi
        frames = process_frames[p][:]

        # Losowo tasuje klatki, aby rozdział między fazy był losowy
        random.shuffle(frames)

        # Tworzy listę pustych list — po jednej dla każdej fazy
        phase_frames = [[] for _ in range(phases)]

        # Iteruje przez wszystkie klatki przypisane danemu procesowi
        for idx_frame, frame in enumerate(frames):
            # Losowo wybiera fazę, do której zostanie przypisana dana klatka
            phase = random.randint(0, phases - 1)
            # Dodaje klatkę do odpowiedniej fazy
            phase_frames[phase].append(frame)

        # Przypisuje listę klatek podzielonych na fazy do bieżącego procesu
        process_phase_frames[p] = phase_frames

    #------------------------------------------------------------------------------------------    

    # 3. Przydziel miejsca (indeksy requestów) poszczególnym procesom z uwzględnieniem udziałów
    #------------------------------------------------------------------------------------------

    # Tworzy listę indeksów wszystkich żądań (od 0 do total_requests - 1)
    all_request_indices = list(range(total_requests))

    # Losowo mieszam indeksy żądań, aby przypisanie do procesów było losowe
    random.shuffle(all_request_indices)

    # Oblicza, ile żądań przypada na każdy proces na podstawie zadanych proporcji
    process_request_counts = [int(total_requests * p) for p in process_proportions]

    # Koryguje ewentualne różnice wynikające z zaokrągleń — dodaje brakujące żądania do pierwszego procesu
    diff = total_requests - sum(process_request_counts)
    process_request_counts[0] += diff

    # Tworzy słownik, który przypisuje każdemu procesowi odpowiednią listę indeksów żądań
    #Tutaj jest prowadzone fazowanie, losowo już, teoretycznie można by jeszcze dokładniej ale po co
    process_request_indices = {}
    idx = 0
    for p, count in enumerate(process_request_counts):
        # Przypisuje losowy, ale posortowany zakres indeksów żądań do procesu `p`
        process_request_indices[p] = sorted(all_request_indices[idx:idx + count])
        # Przesuwa indeks do początku kolejnego bloku żądań
        idx += count

    #------------------------------------------------------------------------------------------
    
    #4 TUTAJ dodajemy indywidualne przedziały fazowe dla każdego procesu ---
    #------------------------------------------------------------------------------------------
    # Dla każdego procesu generujemy listę przedziałów fazowych (start, end) na jego indeksy requestów
    process_phase_request_ranges = {}

    for p in range(process_count):
        count = process_request_counts[p]
        base_indices = process_request_indices[p]

        # Jeśli mamy 0 requestów dla procesu, puste fazy
        if count == 0:
            process_phase_request_ranges[p] = []
            continue

        # Dzielimy count na phases segmentów - podobnie jak wcześniej,
        # ale fazy dotyczą tylko indeksów należących do tego procesu
        requests_per_phase = count // phases
        phase_ranges = []
        for ph in range(phases):
            start_idx = ph * requests_per_phase
            # ostatnia faza bierze resztę
            end_idx = (ph + 1) * requests_per_phase if ph < phases - 1 else count
            # zamieniamy indeksy na indeksy globalne requestów z process_request_indices[p]
            if start_idx < count:
                phase_start = base_indices[start_idx]
            else:
                phase_start = base_indices[-1]  # jeśli pusta faza, używamy ostatniego
            if end_idx <= count and end_idx > 0:
                # jeśli end_idx == count, to weź ostatni + 1 albo total_requests
                if end_idx == count:
                    phase_end = base_indices[-1] + 1  # kończymy na 1 za ostatnim
                else:
                    phase_end = base_indices[end_idx]
            else:
                phase_end = base_indices[-1] + 1

            phase_ranges.append((phase_start, phase_end))

        process_phase_request_ranges[p] = phase_ranges
    #------------------------------------------------------------------------------------------

    # 5. Wypełnij tablicę requestów stronami z faz, zgodnie z fazą w czasie (indeksie)
    #------------------------------------------------------------------------------------------

    # Tworzymy listę na wszystkie żądania – indeksowana globalnie, każde pole będzie wypełnione później
    requests = [None] * total_requests

    # Iterujemy po wszystkich procesach
    for p in range(process_count):
        # Pobieramy listę indeksów żądań przypisanych do procesu p
        indices = process_request_indices[p]

        # Słownik: faza → lista indeksów żądań, które należą do tej fazy
        phase_to_indices = defaultdict(list)

        # Pobieramy listę zakresów (start, end) dla każdej fazy danego procesu
        phase_ranges = process_phase_request_ranges[p]

        # Dla każdego indeksu żądania przypisanego do procesu
        for i in indices:
            assigned = False  # Flaga mówiąca, czy udało się przypisać żądanie do jakiejś fazy

            # Sprawdzamy, do którego zakresu fazowego należy dany indeks
            for ph, (start, end) in enumerate(phase_ranges):
                if start <= i < end:
                    # Jeśli indeks żądania pasuje do zakresu fazy ph → przypisz go
                    phase_to_indices[ph].append(i)
                    assigned = True
                    break

            if not assigned:
                # Jeżeli żądanie nie pasowało do żadnej fazy (możliwy edge case),
                # przypisujemy je do ostatniej fazy jako zapas
                phase_to_indices[phases - 1].append(i)

        # Dla każdej fazy, która ma przypisane żądania
        for ph, inds in phase_to_indices.items():
            # Pobieramy dostępne ramki (strony) przypisane do tej fazy i procesu
            frames_for_phase = process_phase_frames[p][ph]

            # Jeśli faza nie ma przypisanych żadnych stron, rzucamy wyjątek — to błąd w danych wejściowych
            if not frames_for_phase:
                raise ValueError(f"Proces {p} faza {ph} nie ma żadnych stron!")

            # Dla każdego żądania przypisanego do tej fazy, losujemy stronę z przydzielonych
            for i_req in inds:
                page = random.choice(frames_for_phase)  # Losowo wybierz stronę z dostępnych dla tej fazy
                requests[i_req] = (p, page, i_req, ph)   # Zapisz żądanie w formacie: (proces, strona, indeks, faza)

    #------------------------------------------------------------------------------------------

    # 6. Wypisz wyniki
    #------------------------------------------------------------------------------------------
    print("Procesy i ich strony (ramki):")
    for p in range(process_count):
        print(f"Proces P{p}: {sorted(process_frames[p])}")

    print("\nFazy i przypisane strony dla każdego procesu:")
    for p in range(process_count):
        for ph in range(phases):
            print(f"Proces P{p} - Faza {ph}: {sorted(process_phase_frames[p][ph])}")

    print("\nWygenerowane requesty:")
    for r in sorted(requests, key=lambda x: x[2]):
        print(f"Request(P{r[0]}, Page{r[1]}, Time{r[2]}, Faza{r[3]})")
    #------------------------------------------------------------------------------------------
    # Oblicz liczbę ramek przypisaną każdemu procesowi
    frame_alloc = [len(process_frames[p]) for p in range(process_count)]

    return requests, frame_alloc

