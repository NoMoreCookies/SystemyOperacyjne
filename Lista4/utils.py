from collections import deque
import random
# --- Algorytmy ---
#FIFO
#------------------------------------------------
class FIFO:
    def __init__(self, capacity):
        # Maksymalna liczba stron, które mogą się zmieścić w pamięci
        self.capacity = capacity

        # Kolejka FIFO do śledzenia kolejności wczytanych stron
        self.queue = deque()

        # Zbiór stron aktualnie załadowanych do pamięci (dla szybkiego sprawdzania obecności)
        self.pages = set()

    def request(self, page):
        # Jeśli żądana strona już jest w pamięci, nie ma potrzeby nic zmieniać
        if page in self.pages:
            return False  # Nie było błędu strony (page fault)

        # Jeśli mamy jeszcze miejsce w pamięci, po prostu dodajemy stronę
        if len(self.queue) < self.capacity:
            self.queue.append(page)     # Dodaj stronę na koniec kolejki
            self.pages.add(page)        # Dodaj stronę do zbioru aktualnych stron
            return True                 # Nastąpił błąd strony (page fault) (No bo jej nie było)

        # Jeśli pamięć jest pełna, usuwamy najstarszą stronę (z początku kolejki)
        old = self.queue.popleft()      # Usuń najstarszą stronę
        self.pages.remove(old)          # Usuń ją również ze zbioru dostępnych stron

        # Dodaj nową stronę do kolejki i zbioru
        self.queue.append(page)
        self.pages.add(page)

        return True  # Błąd strony – bo załadowaliśmy nową stronę, usuwając
#------------------------------------------------

#SECOND_CHANCE
#------------------------------------------------
class SecondChance:
    def __init__(self, capacity):
        # Maksymalna liczba stron w pamięci
        self.capacity = capacity

        # Kolejka stron (FIFO), ale z mechanizmem "drugiej szansy"
        self.queue = deque()

        # Mapa: strona → bit referencyjny (0 lub 1)
        self.reference_bits = {}

    def request(self, page):
        # Jeżeli strona już znajduje się w pamięci, dajemy jej "drugą szansę"
        if page in self.reference_bits:
            self.reference_bits[page] = 1  # Ustawiamy bit referencyjny na 1
            return False  # Nie ma błędu strony

        # Jeżeli mamy jeszcze miejsce w pamięci, dodajemy stronę bez zastępowania
        if len(self.queue) < self.capacity:
            self.queue.append(page)         # Dodaj stronę na koniec kolejki
            self.reference_bits[page] = 1   # Ustaw bit referencyjny
            return True                     # Błąd strony (page fault)

        # Jeżeli pamięć jest pełna, szukamy strony do usunięcia z bitem 0
        while self.reference_bits[self.queue[0]] == 1:
            # Strona ma ustawiony bit referencyjny: dajemy jej drugą szansę
            p = self.queue.popleft()       # Usuń z początku kolejki
            self.reference_bits[p] = 0     # Resetuj bit referencyjny
            self.queue.append(p)           # Dodaj z powrotem na koniec

        # Strona na początku kolejki ma bit 0 – usuwamy ją
        old = self.queue.popleft()         # Usuń starą stronę
        del self.reference_bits[old]       # Usuń ją również z mapy bitów

        # Dodajemy nową stronę do pamięci
        self.queue.append(page)
        self.reference_bits[page] = 1      # Ustaw bit referencyjny dla nowej strony

        return True  # Błąd strony – musieliśmy załadować nową stronę, usuwając inną
#------------------------------------------------

#LRU
#------------------------------------------------
class LRU:
    def __init__(self, capacity):
        # Maksymalna liczba stron, które mogą być przechowywane w pamięci
        self.capacity = capacity

        # Słownik: strona → licznik (ile żądań temu ostatnio była używana)
        self.pages = {}

    def request(self, page):
        # Zwiększamy liczniki dla wszystkich stron — każda "starzeje się" o 1
        for p in self.pages:
            self.pages[p] += 1

        # Jeśli strona już jest w pamięci
        if page in self.pages:
            self.pages[page] = 0  # Resetujemy licznik dla tej strony (użyta właśnie teraz)
            return False  # Nie wystąpił błąd strony

        # Jeśli mamy jeszcze miejsce, dodajemy stronę bez usuwania
        if len(self.pages) < self.capacity:
            self.pages[page] = 0  # Nowa strona, właśnie użyta
            return True  # Błąd strony (page fault)

        # Pamięć jest pełna — musimy usunąć stronę najmniej niedawno używaną
        # Szukamy strony z największym licznikiem (najdawniej używana)
        lru_page = max(self.pages.items(), key=lambda x: x[1])[0]

        # Usuwamy najstarszą stronę z pamięci
        del self.pages[lru_page]

        # Dodajemy nową stronę, z licznikiem ustawionym na 0 (bo używana teraz)
        self.pages[page] = 0

        return True  # Błąd strony — bo załadowaliśmy nową, usuwając inną
#------------------------------------------------

#OPT
#------------------------------------------------
class OPT:
    def __init__(self, capacity, all_requests=None, pid=None):
        # Maksymalna liczba stron w pamięci
        self.capacity = capacity

        # Lista stron aktualnie znajdujących się w pamięci
        self.pages = []

        # Lista wszystkich przyszłych żądań w symulacji
        # (używana do przewidywania, która strona będzie potrzebna najpóźniej)
        self.all_requests = all_requests

        # Identyfikator procesu (potrzebny, aby filtrować tylko jego żądania)
        self.pid = pid

    def request(self, page, current_time):
        # Jeśli żądana strona już jest w pamięci, nie ma błędu strony
        if page in self.pages:
            return False

        # Jeśli w pamięci jest jeszcze miejsce, po prostu dodajemy stronę
        if len(self.pages) < self.capacity:
            self.pages.append(page)
            return True  # Błąd strony — strona została załadowana

        # Zbieramy przyszłe żądania tego samego procesu (od current_time + 1 do końca)
        future_references = [
            req[1] for req in self.all_requests[current_time + 1:]
            if req[0] == self.pid
        ]

        # Dla każdej strony w pamięci sprawdzamy, kiedy zostanie użyta w przyszłości
        # Jeśli strona się już nie pojawi, przypisujemy jej inf (nieskończoność)
        indices = []
        for p in self.pages:
            try:
                idx = future_references.index(p)  # pozycja w przyszłości
            except ValueError:
                idx = float('inf')  # strona nie zostanie więcej użyta
            indices.append(idx)

        # Wybieramy stronę, która będzie potrzebna najpóźniej lub wcale
        to_remove = indices.index(max(indices))

        # Zastępujemy ją nową stroną
        self.pages[to_remove] = page

        return True  # Błąd strony — nowa strona została załadowana
#------------------------------------------------

#RANDOM #USUWANIE LOSOWEJ STRONY, NIC NADZWYCZAJNEGO ('-')
#------------------------------------------------
class RandomAlg:
    def __init__(self, capacity):
        self.capacity = capacity
        self.pages = set()
    def request(self, page):
        if page in self.pages:
            return False
        if len(self.pages) < self.capacity:
            self.pages.add(page)
            return True
        victim = random.choice(list(self.pages))
        self.pages.remove(victim)
        self.pages.add(page)
        return True
#------------------------------------------------

# --- Menedżer procesu ze sterowaniem PPF ---
#------------------------------------------------
"""
PROCESS MANAGER ODPOWIADA ZA POMOC  OGARNIANIU TYCH PROCESÓW,
NP: 
JEGO NUMER
ILE MA RAMEK NA POCZĄTKU
DO ALGORYTMU PPF ILE JEST BŁĘDÓW W POPRZEDNICH STRONACH
CZY JEST AKTYWNY
NOI PRZEKAZANIE JESZCZE WSZYSTKICH REQUESTÓW
"""
class ProcessMemoryManager:
    def __init__(self, pid, init_frames, window_size, AlgorithmClass, all_requests=None):
        
        #PARAMETRY ALGORYTMU
        #----------------------------------------------------------------------------
        self.pid = pid
        self.frames = init_frames
        self.window_size = window_size
        self.page_faults_window = deque(maxlen=window_size)
        self.total_faults = 0
        self.paused = False
        self.all_requests = all_requests
        #----------------------------------------------------------------------------

        # Tworzymy instancję algorytmu stronicowania
        #DLA OPT INACZEJ BO TAM TRZEBA JESZCZE SPRAWDZIĆ  TĄ PRZYSZŁOŚĆ
        #----------------------------------------------------------------------------
        if AlgorithmClass == OPT:
            self.algorithm = AlgorithmClass(init_frames, all_requests=all_requests, pid=pid)
        else:
            self.algorithm = AlgorithmClass(init_frames)
        #----------------------------------------------------------------------------    

    #TUTAJ OGARNIĘTE JEST DEALOWANIE Z REQUESTAMI
    #----------------------------------------------------------------------------    
    def handle_request(self, page, current_time):
        # Jeśli symulacja jest wstrzymana (paused), nie przetwarzamy requestu,
        # ale odnotowujemy brak błędu strony (0) w oknie statystyk
        if self.paused:
            self.page_faults_window.append(0)
            return False  # Brak zmiany, request nie jest obsługiwany

        # Jeśli algorytm to OPT, wywołujemy request z dwoma argumentami (page i current_time),
        # bo OPT potrzebuje znać aktualny czas, aby przewidywać przyszłość
        if isinstance(self.algorithm, OPT):
            fault = self.algorithm.request(page, current_time)
        else:
            # Dla pozostałych algorytmów (FIFO, LRU, SecondChance) wywołujemy request z jednym argumentem
            fault = self.algorithm.request(page)

        # Aktualizujemy okno statystyk błędów stron:
        # dodajemy 1 jeśli wystąpił błąd strony, w przeciwnym razie 0
        self.page_faults_window.append(1 if fault else 0)

        # Jeśli wystąpił błąd strony, zwiększamy licznik całkowitych błędów
        if fault:
            self.total_faults += 1

        # Zwracamy informację, czy nastąpił błąd strony (True/False)
        return fault

    #----------------------------------------------------------------------------

    #SPRAWDZAMY OBECNIE JAKI JEST WSPÓŁCZYNNIK BŁĘDÓW
    #------------------------------------------------
    def get_ppf(self):
        # Sprawdza, czy okno błędów stron (page_faults_window) jest puste
        if len(self.page_faults_window) == 0:
            # Jeśli nie ma żadnych danych (żadnych żądań), zwraca 0.0 — brak błędów
            return 0.0
        
        # W przeciwnym razie oblicza stosunek liczby błędów stron (suma jedynek w oknie)
        # do całkowitej liczby obserwowanych żądań (długość okna)
        # czyli średnią częstość występowania błędów stron (page fault frequency)
        return sum(self.page_faults_window) / self.window_size

    #------------------------------------------------

    #------------------------------------------------
    def update_frames(self, new_frame_count, AlgorithmClass):
        # Aktualizujemy liczbę dostępnych ramek pamięci na nową wartość
        self.frames = new_frame_count

        # Resetujemy algorytm zarządzania pamięcią, tworząc jego nową instancję
        # Jeśli wybrany algorytm to OPT, przekazujemy dodatkowo listę wszystkich żądań oraz PID procesu,
        # ponieważ OPT potrzebuje tych informacji do działania
        if AlgorithmClass == OPT:
            self.algorithm = AlgorithmClass(new_frame_count, all_requests=self.all_requests, pid=self.pid)
        else:
            # Dla innych algorytmów (FIFO, LRU, SecondChance) tworzymy instancję tylko z liczbą ramek
            self.algorithm = AlgorithmClass(new_frame_count)

        # Czyscimy okno błędów stron, ponieważ resetujemy symulację / algorytm
        self.page_faults_window.clear()
    #------------------------------------------------
#------------------------------------------------