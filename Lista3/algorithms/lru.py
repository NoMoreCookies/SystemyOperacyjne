
def lru(ciag_odwolan, rozmiar_pamieci):
    #DEFINIOWANIE ZM.POMOCNICZYCH
    #------------------------------------------------------
    pamiec = {} 
    bledy = 0
    #------------------------------------------------------

    for strona in ciag_odwolan:

        # ZWIĘKSZAMY CZAS OD OSTATNIEGO UŻYCIA KAŻDEJ ZE STRON
        #---------------------------------------------
        for s in pamiec:
            pamiec[s] += 1
        #---------------------------------------------

        #OGARNIANIE STRON W PAMIĘCI
        #---------------------------------------------
        if strona in pamiec:
            pamiec[strona] = 0  # użyta – resetujemy licznik
        else:
            bledy += 1
            if len(pamiec) < rozmiar_pamieci:
                pamiec[strona] = 0
            else:
                # znajdź stronę najdłużej nieużywaną
                do_usuniecia = max(pamiec.items(), key=lambda x: x[1])[0]
                del pamiec[do_usuniecia]
                pamiec[strona] = 0
        #---------------------------------------------

    return bledy
