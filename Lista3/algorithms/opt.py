def opt(ciag_odwolan, rozmiar_pamieci):
    pamiec = []
    bledy = 0

    for i, strona in enumerate(ciag_odwolan):
        #SPRAWDZAM CZY STRONA JEST JUŻ W PAMIĘCI
        #---------------------------------------------
        if strona in pamiec:
            continue  # strona już w pamięci
        #---------------------------------------------

        #JEŻELI NIE MA STRONY W PAMIĘCI
        #---------------------------------------------
        bledy += 1

        if len(pamiec) < rozmiar_pamieci:
            pamiec.append(strona)
        else:
            przyszle = ciag_odwolan[i+1:]
            indeksy = []
            for s in pamiec:
                try:
                    indeksy.append(przyszle.index(s))
                except ValueError:
                    indeksy.append(float('inf')) 

            #WYBIERAM STRONĘ, KTÓRA WYSTĘPUJĘ NAJDALEJ W PRZYSZŁOŚCI
            #---------------------------------------------
            index_do_usuniecia = indeksy.index(max(indeksy))
            pamiec[index_do_usuniecia] = strona
            #---------------------------------------------
        #---------------------------------------------

    #ZWRACAM
    #---------------------------------------------
    return bledy
    #---------------------------------------------

