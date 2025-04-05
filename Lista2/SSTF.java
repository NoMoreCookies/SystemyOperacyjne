import java.util.List;
import java.util.ArrayList;

public class SSTF {
    // ---------------------------------------- Metoda wykonująca algorytm SSTF (Shortest Seek Time First) ----------------------------------------
    public static long[] execute(List<Request> requests)
    {
        long totalWaitingTime = 0;  // Zmienna do sumowania czasów oczekiwania
        long maxWaitingTime = Long.MIN_VALUE;  // Inicjalizacja maksymalnego czasu oczekiwania
        long minWaitingTime = Long.MAX_VALUE;  // Inicjalizacja minimalnego czasu oczekiwania
        int currentCylinder = 0;  // Początkowa pozycja głowicy (zakładamy, że głowica zaczyna od cylindra 0)
        long totalCylinderChanges = 0;  // Suma zmian cylindra (odległość)

        long currentTime = 0;  // Czas, w którym system jest gotów obsługiwać żądanie

        // Kopiujemy żądania, żeby nie modyfikować oryginalnej listy
        List<Request> remainingRequests = new ArrayList<>(requests);

        // ---------------------------------------- Dopóki są żądania do obsłużenia ----------------------------------------
        while (!remainingRequests.isEmpty()) {
            // Wybieramy najbliższe żądanie (najmniejsza odległość)
            Request closestRequest = findClosestRequest(remainingRequests, currentCylinder);

            // Jeżeli żądanie przybywa po czasie bieżącym, ustawiamy currentTime na czas przybycia żądania
            currentTime = Math.max(currentTime, closestRequest.getArrivalTime());  // Ustawiamy currentTime na czas przybycia

            // Czas oczekiwania = czas, w którym żądanie jest obsługiwane - czas zgłoszenia
            long waitingTime = currentTime - closestRequest.getArrivalTime();  // Obliczamy czas oczekiwania
            closestRequest.setWaitingTime(waitingTime);  // Ustawiamy czas oczekiwania w obiekcie Request
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

            // Liczymy zmianę cylindra (odległość)
            long cylinderChange = Math.abs(closestRequest.getCylinder() - currentCylinder);  // Obliczamy zmianę cylindra (odległość)
            totalCylinderChanges += cylinderChange;  // Sumujemy odległość
            currentCylinder = closestRequest.getCylinder();  // Ustawiamy nową pozycję głowicy

            // Usuwamy obsłużone żądanie z listy
            remainingRequests.remove(closestRequest);  // Usuwamy żądanie z listy po obsłużeniu
        }
        // ------------------------------------------------------------------------------------------------------------------

        // ---------------------------------------- Obliczamy średni czas oczekiwania ----------------------------------------
        long averageWaitingTime = totalWaitingTime / requests.size();  // Obliczamy średni czas oczekiwania

        // Zwracamy tablicę z wartościami: maxWaitingTime, minWaitingTime, averageWaitingTime, totalCylinderChanges, startingCylinder
        return new long[] {maxWaitingTime, minWaitingTime, averageWaitingTime, totalCylinderChanges, 0};  // 0 - początkowa pozycja cylindra (zakładamy cylinder 0)
    }
    // ------------------------------------------------------------------------------------------------------------------

    // ---------------------------------------- Pomocnicza metoda do znalezienia najbliższego żądania w stosunku do obecnej pozycji głowicy ----------------------------------------
    private static Request findClosestRequest(List<Request> requests, int currentCylinder) {
        Request closestRequest = requests.get(0);  // Inicjalizujemy najbliższe żądanie na pierwszym elemencie
        int minDistance = Math.abs(closestRequest.getCylinder() - currentCylinder);  // Obliczamy początkową odległość

        for (Request req : requests)
        {
            int distance = Math.abs(req.getCylinder() - currentCylinder);  // Obliczamy odległość od obecnej pozycji głowicy
            if (distance < minDistance)
            {
                closestRequest = req;  // Ustawiamy nowe żądanie jako najbliższe
                minDistance = distance;  // Aktualizujemy minimalną odległość
            }
        }

        return closestRequest;  // Zwracamy najbliższe żądanie
    }
    // ------------------------------------------------------------------------------------------------------------------
}
