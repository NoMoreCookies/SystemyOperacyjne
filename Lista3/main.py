# main.py

from generator import generuj_ciag_odwolan
from config import ROZMIAR_PAMIECI_FIZYCZNEJ
from config import LICZBA_STRON_WIRTUALNYCH
from algorithms.fifo import fifo
from algorithms.lru import lru
from algorithms.opt import opt
from algorithms.lfu import lfu
from algorithms.rand import rand
from utils import wypisz_wyniki, ustaw_ziarno
from config import LOSOWE_ZIARNO
import matplotlib.pyplot as plt

# Listy do wyników
fifo_wyniki = []
lru_wyniki = []
opt_wyniki = []
lfu_wyniki = []
rand_wyniki = []

ustaw_ziarno(LOSOWE_ZIARNO)
ciag = generuj_ciag_odwolan()

#WYKRES L.BŁĘDÓW DLA RÓŻCZNEJ ILOŚCI PAMIĘCI FIZYCZNEJ
#---------------------------------------------
L_RAMEK= [1,2,4,8,10,12,15,16,20,30,40,50]
for i in L_RAMEK:

    ROZMIAR_PAMIECI_FIZYCZNEJ=i
    print(i)
    print("---------------------------------------------------------")

    wyniki = {
        "FIFO": fifo(ciag, ROZMIAR_PAMIECI_FIZYCZNEJ),
        "LRU": lru(ciag, ROZMIAR_PAMIECI_FIZYCZNEJ),
        "OPT": opt(ciag, ROZMIAR_PAMIECI_FIZYCZNEJ),
        "LFU": lfu(ciag, ROZMIAR_PAMIECI_FIZYCZNEJ),
        "RAND": rand(ciag, ROZMIAR_PAMIECI_FIZYCZNEJ),
    }
    fifo_wyniki.append(wyniki["FIFO"])
    lru_wyniki.append(wyniki["LRU"])
    opt_wyniki.append(wyniki["OPT"])
    lfu_wyniki.append(wyniki["LFU"])
    rand_wyniki.append(wyniki["RAND"])
    print(fifo_wyniki)
    wypisz_wyniki(wyniki)

# Tworzenie wykresu
plt.figure(figsize=(12, 6))
plt.plot(L_RAMEK, fifo_wyniki, label='FIFO', marker='o')
plt.plot(L_RAMEK, lru_wyniki, label='LRU', marker='s')
plt.plot(L_RAMEK, opt_wyniki, label='OPT', marker='^')
plt.plot(L_RAMEK, lfu_wyniki, label='LFU', marker='D')
plt.plot(L_RAMEK, rand_wyniki, label='RAND', marker='x')

plt.title('Liczba błędów stron vs. rozmiar pamięci fizycznej (PAMIĘĆ WIRTUALNA CONST u nas 100)')
plt.xlabel('Liczba ramek (rozmiar pamięci fizycznej)')
plt.ylabel('Liczba błędów stron')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
#---------------------------------------------



#WYKRES DLA RÓŻNEJ PAMIĘCI WIRTUALNEJ
#---------------------------------------------
ROZMIAR_PAMIECI_FIZYCZNEJ = 19

R_WIRTUALNEJ = [100,150,200,250,300,350,400,450,500]
# Listy do wyników
fifo_wyniki = []
lru_wyniki = []
opt_wyniki = []
lfu_wyniki = []
rand_wyniki = []
for i in R_WIRTUALNEJ:

    LICZBA_STRON_WIRTUALNYCH=i
    print(i)
    print("---------------------------------------------------------")

    wyniki = {
        "FIFO": fifo(ciag, ROZMIAR_PAMIECI_FIZYCZNEJ),
        "LRU": lru(ciag, ROZMIAR_PAMIECI_FIZYCZNEJ),
        "OPT": opt(ciag, ROZMIAR_PAMIECI_FIZYCZNEJ),
        "LFU": lfu(ciag, ROZMIAR_PAMIECI_FIZYCZNEJ),
        "RAND": rand(ciag, ROZMIAR_PAMIECI_FIZYCZNEJ),
    }
    fifo_wyniki.append(wyniki["FIFO"])
    lru_wyniki.append(wyniki["LRU"])
    opt_wyniki.append(wyniki["OPT"])
    lfu_wyniki.append(wyniki["LFU"])
    rand_wyniki.append(wyniki["RAND"])
    print(fifo_wyniki)
    wypisz_wyniki(wyniki)

# Tworzenie wykresu
plt.figure(figsize=(12, 6))
plt.plot(R_WIRTUALNEJ, fifo_wyniki, label='FIFO', marker='o')
plt.plot(R_WIRTUALNEJ, lru_wyniki, label='LRU', marker='s')
plt.plot(R_WIRTUALNEJ, opt_wyniki, label='OPT', marker='^')
plt.plot(R_WIRTUALNEJ, lfu_wyniki, label='LFU', marker='D')
plt.plot(R_WIRTUALNEJ, rand_wyniki, label='RAND', marker='x')

plt.title('Liczba błędów stron vs. rozmiar pamięci WIRTUALNEJ (PAMIĘĆ FIZYCZNA CONST u nas 10)')
plt.xlabel('Liczba ramek (rozmiar pamięci fizycznej)')
plt.ylabel('Liczba błędów stron')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
#---------------------------------------------