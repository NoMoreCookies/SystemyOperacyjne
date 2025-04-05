import java.util.List;

public class FCFS
{
    // ---------------------------------------- Metoda wykonująca algorytm FCFS ----------------------------------------
    public static long[] execute(List<Request> requests) {
        // Sortowanie żądań według arrivalTime (czas zgłoszenia)

        requests.sort(null);  // Sortowanie po czasie przybycia

        /// POLA KLASY
        //--------------------------------------------------------------------------------------------------------------
        long totalWaitingTime = 0;  // Zmienna do sumowania czasów oczekiwania
        long maxWaitingTime = Long.MIN_VALUE;  // Inicjalizacja maksymalnego czasu oczekiwania
        long minWaitingTime = Long.MAX_VALUE;  // Inicjalizacja minimalnego czasu oczekiwania

        long currentTime = 0;  // Czas startowy systemu
        int currentCylinder = 0;  // Obecny cylinder
        long totalCylinderChanges = 0;  // Suma zmian cylindra (droga jaką przeszła nasza głowica)
        //--------------------------------------------------------------------------------------------------------------

        // ---------------------------------------- Obliczamy czas oczekiwania i zmiany cylindra dla każdego żądania ----------------------------------------
        for (Request req : requests)
        {
            // Jeżeli żądanie przybywa po czasie bieżącym, ustawiamy currentTime na czas przybycia żądania
            currentTime = Math.max(currentTime, req.getArrivalTime());  // Sprawdzamy, czy żądanie przybyło po czasie

            // Czas oczekiwania = czas, w którym żądanie jest obsługiwane - czas zgłoszenia
            long waitingTime = currentTime - req.getArrivalTime();  // Obliczamy czas oczekiwania
            req.setWaitingTime(waitingTime);  // Ustawiamy czas oczekiwania w obiekcie Request
            totalWaitingTime += waitingTime;  // Sumujemy czas oczekiwania

            // Aktualizujemy max i min czas oczekiwania
            if (waitingTime > maxWaitingTime)
            {
                maxWaitingTime = waitingTime;  // Aktualizujemy max czas oczekiwania
            }
            if (waitingTime < minWaitingTime)
            {
                minWaitingTime = waitingTime;  // Aktualizujemy min czas oczekiwania
            }

            // Po obsłudze żądania, czas systemu (currentTime) jest zwiększany o czas realizacji operacji
            currentTime += 1;  // Zakładając, że każda operacja trwa 1 jednostkę czasu

            // Liczenie zmiany cylindra (odległość)
            long cylinderChange = Math.abs(req.getCylinder() - currentCylinder);  // Obliczamy zmianę cylindra (odległość)
            totalCylinderChanges += cylinderChange;  // Sumujemy odległość
            currentCylinder = req.getCylinder();  // Ustawiamy nową pozycję głowicy
        }

        // ---------------------------------------- Obliczamy średni czas oczekiwania ----------------------------------------
        long averageWaitingTime = totalWaitingTime / requests.size();  // Obliczamy średni czas oczekiwania

        // Zwracamy tablicę z wartościami: maxWaitingTime, minWaitingTime, averageWaitingTime, totalCylinderChanges, startingCylinder
        return new long[] {maxWaitingTime, minWaitingTime, averageWaitingTime, totalCylinderChanges, 0};  // 0 - początkowa pozycja cylindra (zakładamy cylinder 0)
    }
    // ------------------------------------------------------------------------------------------------------------------
}
