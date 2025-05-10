# algorithms/fifo.py

from collections import deque

#fifo.py
#---------------------------------------------
def fifo(ciag_odwolan, rozmiar_pamieci):

    #ZM POMOCNICZE
    #---------------------------------------------
    pamiec = []  # lista par (strona, wiek)
    bledy = 0
    #---------------------------------------------

    for strona in ciag_odwolan:
        # Z KAŻDYM WYWOŁANIEM ZWIĘKSZA SIĘ WIEK WSZYSTKICH STRON
        #---------------------------------------------
        pamiec = [(s, wiek + 1) for s, wiek in pamiec]
        #---------------------------------------------

        # Sprawdź, czy strona już jest w pamięci JEŻELI JEST, TO IDZIEMY DALEJ , DO KOLEJNEJ STRONY W KOLEJCE
        #---------------------------------------------
        indeks = next((i for i, (s, _) in enumerate(pamiec) if s == strona), None)
        
        if indeks is not None:
            continue  
        #---------------------------------------------


        #JEŻELI STRONY NIE MA W PAMIĘCI
        #---------------------------------------------
        bledy += 1
        #---------------------------------------------

        #JEŻELI MAMY MIEJSCE W PAMIĘCI TO DODAJEMY STRONĘ, JEŻELI NIE MAMY, TO USUWAMY NAJSTARSZĄ
        if len(pamiec) < rozmiar_pamieci:
            # Jest miejsce – dodaj nową stronę
            #---------------------------------------------
            pamiec.append((strona, 0))
            #---------------------------------------------
        else:
            # Wybierz stronę o największym wieku do usunięcia
            #---------------------------------------------
            do_usuniecia = max(pamiec, key=lambda x: x[1])
            pamiec.remove(do_usuniecia)
            pamiec.append((strona, 0))
            #---------------------------------------------


    #ZWRACAMY ILOŚĆ BŁĘDÓW
    #---------------------------------------------
    return bledy
    #---------------------------------------------

#---------------------------------------------