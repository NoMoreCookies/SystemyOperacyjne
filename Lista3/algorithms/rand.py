
import random

def rand(ciag_odwolan, rozmiar_pamieci):
    pamiec = set()  # zbiór stron w pamięci
    bledy = 0

    for strona in ciag_odwolan:
        if strona not in pamiec:
            bledy += 1
            if len(pamiec) < rozmiar_pamieci:
                pamiec.add(strona)
            else:
                # Wybieramy losową stronę do usunięcia
                strona_do_usuniecia = random.choice(list(pamiec))
                pamiec.remove(strona_do_usuniecia)
                pamiec.add(strona)

    return bledy
