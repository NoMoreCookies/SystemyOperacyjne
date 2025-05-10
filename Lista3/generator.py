# generator.py

import random
from config import (
    LICZBA_STRON_WIRTUALNYCH,
    LICZBA_FAZ,
    DLUGOSC_FAZY,
    MIN_PODZBIOR,
    MAX_PODZBIOR
)
from utils import losuj_podzbior_stron, generuj_faze
# długość ciągu to LICZBA_FAZ × DLUGOSC_FAZY
def generuj_ciag_odwolan():
    """Generuje pełny ciąg odwołań z uwzględnieniem zasady lokalności."""
    ciag_odwolan = []

    for _ in range(LICZBA_FAZ):
        podzbior = losuj_podzbior_stron(LICZBA_STRON_WIRTUALNYCH, MIN_PODZBIOR, MAX_PODZBIOR)
        faza = generuj_faze(podzbior, DLUGOSC_FAZY)
        ciag_odwolan.extend(faza)

    return ciag_odwolan
