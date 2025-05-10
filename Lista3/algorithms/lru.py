# algorithms/lru_z_licznikami.py

def lru(ciag_odwolan, rozmiar_pamieci):
    pamiec = {}  # słownik: strona -> licznik czasu nieużycia
    bledy = 0

    for strona in ciag_odwolan:

        # Zwiększ czas nieużycia dla wszystkich stron
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
