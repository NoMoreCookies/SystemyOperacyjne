import java.util.List;
import java.util.ArrayList;

public class SCAN {
    // ---------------------------------------- Metoda wykonująca algorytm SCAN ----------------------------------------
    public static long[] execute(List<Request> requests) {
        // Sprawdzamy, czy lista żądań jest pusta
        if (requests.isEmpty()) {
            return new long[] {0, 0, 0, 0, 0}; // Zwracamy 0 dla wyników, jeśli nie ma żądań
        }

        int size = (requests.size());
        long totalWaitingTime = 0;
        long maxWaitingTime = Long.MIN_VALUE;
        long minWaitingTime = Long.MAX_VALUE;
        int currentCylinder = 0;
        long totalCylinderChanges = 0;
        long currentTime = 0;
        boolean movingRight = true; // Zmienna do określenia kierunku ruchu głowicy (początkowo w prawo)

        // Lista do przechowywania dostępnych żądań
        List<Request> currentRequests = new ArrayList<>();

        // ---------------------------------------- Obsługuje żądania w kierunku SCAN ----------------------------------------
        while (!requests.isEmpty() || !currentRequests.isEmpty())
        {
            System.out.println(requests.size());
            if(!requests.isEmpty() && currentTime<requests.get(0).getArrivalTime()){currentTime = requests.get(0).getArrivalTime();}

            for (Request req : requests) {
                if (req.getArrivalTime() <= currentTime ) {
                    currentRequests.add(req);  // Dodajemy dostępne żądania
                }
            }

            // Jeśli lista currentRequests nie jest pusta, kontynuujemy przetwarzanie
            if (!currentRequests.isEmpty()) {
                // Sortowanie żądań według pozycji cylindra, zależnie od kierunku
                if (movingRight) {
                    currentRequests.sort((r1, r2) -> Integer.compare(r1.getCylinder(), r2.getCylinder()));
                } else {
                    currentRequests.sort((r1, r2) -> Integer.compare(r2.getCylinder(), r1.getCylinder()));
                }

                // Wybieramy najbliższe żądanie
                Request closestRequest = currentRequests.get(0);

                // Ustawiamy czas systemu na czas przybycia żądania, jeśli jest późniejszy
                currentTime = Math.max(currentTime, closestRequest.getArrivalTime());

                // Czas oczekiwania = czas obsługi - czas zgłoszenia
                long waitingTime = currentTime - closestRequest.getArrivalTime();  // Obliczamy czas oczekiwania
                closestRequest.setWaitingTime(waitingTime);  // Ustawiamy czas oczekiwania w obiekcie Request
                totalWaitingTime += waitingTime;  // Sumujemy czas oczekiwania

                // Aktualizujemy max i min czas oczekiwania
                if (waitingTime > maxWaitingTime) maxWaitingTime = waitingTime;  // Sprawdzamy maksymalny czas oczekiwania
                if (waitingTime < minWaitingTime) minWaitingTime = waitingTime;  // Sprawdzamy minimalny czas oczekiwania

                currentTime += 1;  // Zakładając, że każda operacja trwa 1 jednostkę czasu

                // Liczymy zmianę cylindra (odległość)
                totalCylinderChanges += Math.abs(closestRequest.getCylinder() - currentCylinder);
                currentCylinder = closestRequest.getCylinder();  // Ustawiamy nową pozycję głowicy

                // Zmieniamy kierunek głowicy, jeśli dotarliśmy do końca
                if (movingRight && currentCylinder == 180 || !movingRight && currentCylinder == 0) {
                    movingRight = !movingRight;  // Zmiana kierunku
                }

                // Usuwamy obsłużone żądanie z currentRequests
                currentRequests.remove(closestRequest);  // Usuwamy żądanie z listy po obsłużeniu
                requests.remove(closestRequest);
            } else {
                // Jeśli nie ma dostępnych żądań (wszystkie pozostałe nie dotarły jeszcze), możemy zakończyć algorytm
                break;
            }

            // Usuwamy już obsłużone żądania z oryginalnej listy requests
            requests.removeAll(currentRequests);
        }
        // ------------------------------------------------------------------------------------------------------------------

        // ---------------------------------------- Obliczamy średni czas oczekiwania ----------------------------------------
        long averageWaitingTime = totalWaitingTime / size;  // Obliczamy średni czas oczekiwania

        return new long[] {maxWaitingTime, minWaitingTime, averageWaitingTime, totalCylinderChanges, 0};  // 0 - początkowa pozycja cylindra (zakładamy cylinder 0)
    }
    // ------------------------------------------------------------------------------------------------------------------
}
