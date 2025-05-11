# utils.py
'''
PLIK Z POMOCNICZYMI FUNKCJAMI

'''

import random

#DO LOSOWANIA
#---------------------------------------------
def ustaw_ziarno(seed):
    """Ustawia ziarno dla losowości (deterministyczne testy)."""
    random.seed(seed)
#---------------------------------------------

#LOSUJE PODZBIÓR STRON
#---------------------------------------------
def losuj_podzbior_stron(liczba_stron, min_podzbior, max_podzbior):
    """Zwraca losowy podzbiór stron z przestrzeni pamięci wirtualnej."""
    rozmiar = random.randint(min_podzbior, max_podzbior)
    return random.sample(range(liczba_stron), rozmiar)
#---------------------------------------------

#GENEROATOR_FAZ
#---------------------------------------------
def generuj_faze(podzbior, dlugosc_fazy):
    """Generuje listę odwołań do stron tylko z danego podzbioru."""
    return [random.choice(podzbior) for i in range(dlugosc_fazy)]
#---------------------------------------------

#wypisywanie wyników
#---------------------------------------------
def wypisz_wyniki(wyniki):
    """Wypisuje wyniki symulacji w czytelnej formie."""
    for nazwa_alg, blad in wyniki.items():
        print(f"{nazwa_alg}: {blad} błędów stron")
#---------------------------------------------