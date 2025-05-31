from dataclasses import dataclass
#STRONA WRAZ Z CZASEM JEJ PRZYBYCIA OGL DO TYCH ALGORYTMÓW DZIAŁANIA RZECZYWISTEGO SIĘ PRZYDAJE
#------------------------------------------------------------------------------------------
@dataclass(order=True) #TO SORTUJE OBIEKTY PO ARRIVAL TIMIE
class PageReference:
    arrival_time: int
    process_id: int
    page_number: int
#------------------------------------------------------------------------------------------
