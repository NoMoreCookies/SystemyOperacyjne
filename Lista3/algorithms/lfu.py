
from collections import deque

def second_chance(ciag_odwolan, rozmiar_pamieci):
    #ZM.POMOCNICZE
    #---------------------------------------------
    pamiec = deque()  # FIFO
    bity_odwolania = {}  # słownik bitów odwołania
    bledy = 0
    #---------------------------------------------

    for strona in ciag_odwolan:
        # Sprawdzenie, czy strona jest już w pamięci
        #---------------------------------------------
        if strona in bity_odwolania:
            bity_odwolania[strona] = 1  # strona była użyta, ustawiamy bit na 1
            continue  # jeśli strona jest w pamięci, nie ma błędu
        #---------------------------------------------

        # Błąd strony – dodaj nową stronę do pamięci
        #---------------------------------------------
        bledy += 1
        if len(pamiec) < rozmiar_pamieci:
            pamiec.append(strona)
            bity_odwolania[strona] = 1
        else:
            # Musimy usunąć stronę z początku kolejki
            while bity_odwolania[pamiec[0]] == 1:
                # Strona dostaje drugą szansę, przenosimy ją na koniec kolejki
                #---------------------------------------------
                bit = pamiec.popleft()
                bity_odwolania[bit] = 0
                pamiec.append(bit)
                #---------------------------------------------

            #USUWAMY STRONĘ Z BITEM 0 (KOLEJNĄ STRONĘ)
            #------------------------------------------------------
            strona_do_usuniecia = pamiec.popleft()
            del bity_odwolania[strona_do_usuniecia]
            #------------------------------------------------------

            # WSTAWIAMY NOWĄ STRONĘ
            #------------------------------------------------------
            pamiec.append(strona)
            bity_odwolania[strona] = 1
            #------------------------------------------------------

    return bledy

