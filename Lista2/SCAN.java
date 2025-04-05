import java.util.List;

public class SCAN {
    // ---------------------------------------- Metoda wykonująca algorytm SCAN ----------------------------------------
    public static long[] execute(List<Request> requests) {
        // Sprawdzamy, czy lista żądań jest pusta
        if (requests.isEmpty()) {
            return new long[] {0, 0, 0, 0, 0}; // Zwracamy 0 dla wyników, jeśli nie ma żądań
        }

        // Sortowanie żądań według arrivalTime (czas zgłoszenia)
        requests.sort((r1, r2) -> Long.compare(r1.getArrivalTime(), r2.getArrivalTime()));

        ///POLA KLASY
        // ---------------------------------------------------------------------------------------------------------------------
        long totalWaitingTime = 0;  // Zmienna do sumowania czasów oczekiwania
        long maxWaitingTime = Long.MIN_VALUE;  // Inicjalizacja maksymalnego czasu oczekiwania
        long minWaitingTime = Long.MAX_VALUE;  // Inicjalizacja minimalnego czasu oczekiwania

        int currentCylinder = 0;  // Początkowa pozycja głowicy
        long totalCylinderChanges = 0;  // Suma zmian cylindra

        long currentTime = 0;  // Czas, w którym system jest gotów obsługiwać żądanie
        boolean[] movingRight = {true};  // Flaga wskazująca kierunek ruchu głowicy
        // ---------------------------------------------------------------------------------------------------------------------

        // ---------------------------------------- Obsługuje żądania w jednym kierunku ----------------------------------------
        while (!requests.isEmpty()) {
            // W zależności od kierunku, sortujemy żądania
            requests.sort((r1, r2) -> movingRight[0]
                    ? Integer.compare(r1.getCylinder(), r2.getCylinder()) // Porównanie dla "w prawo"
                    : Integer.compare(r2.getCylinder(), r1.getCylinder())); // Porównanie dla "w lewo"

            // Wybieramy najbliższe żądanie
            Request closestRequest = requests.get(0);

            // Jeżeli żądanie przybywa po czasie bieżącym, ustawiamy currentTime na czas przybycia żądania
            currentTime = Math.max(currentTime, closestRequest.getArrivalTime());

            // Czas oczekiwania = czas, w którym żądanie jest obsługiwane - czas zgłoszenia
            long waitingTime = currentTime - closestRequest.getArrivalTime();  // Obliczamy czas oczekiwania
            closestRequest.setWaitingTime(waitingTime);  // Ustawiamy czas oczekiwania w obiekcie Request
            totalWaitingTime += waitingTime;  // Sumujemy czas oczekiwania

            // Aktualizujemy max i min czas oczekiwania
            if (waitingTime > maxWaitingTime) maxWaitingTime = waitingTime;  // Sprawdzamy maksymalny czas oczekiwania
            if (waitingTime < minWaitingTime) minWaitingTime = waitingTime;  // Sprawdzamy minimalny czas oczekiwania

            currentTime += 1;

            // Liczymy zmianę cylindra (odległość)
            totalCylinderChanges += Math.abs(closestRequest.getCylinder() - currentCylinder);  // Sumujemy odległość
            currentCylinder = closestRequest.getCylinder();  // Ustawiamy nową pozycję głowicy

            // Zmieniamy kierunek głowicy, jeśli dotarliśmy do końca
            if (movingRight[0] && closestRequest.getCylinder() == 180 || !movingRight[0] && closestRequest.getCylinder() == 0) {
                movingRight[0] = !movingRight[0];  // Zmiana kierunku
            }

            // Usuwamy obsłużone żądanie z listy
            requests.remove(closestRequest);  // Usuwamy żądanie z listy po obsłużeniu
        }
        // ------------------------------------------------------------------------------------------------------------------

        // ---------------------------------------- Obliczamy średni czas oczekiwania ----------------------------------------
        long averageWaitingTime = 0;  // Zmienna do obliczenia średniego czasu oczekiwania
        if (!requests.isEmpty()) {
            averageWaitingTime = totalWaitingTime / requests.size();  // Obliczamy średni czas oczekiwania
        }

        // Zwracamy tablicę z wartościami: maxWaitingTime, minWaitingTime, averageWaitingTime, totalCylinderChanges, startingCylinder
        return new long[] {maxWaitingTime, minWaitingTime, averageWaitingTime, totalCylinderChanges, 0};  // 0 - początkowa pozycja cylindra (zakładamy cylinder 0)
    }
    // ------------------------------------------------------------------------------------------------------------------
}
