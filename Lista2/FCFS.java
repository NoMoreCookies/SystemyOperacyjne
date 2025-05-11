import java.util.List;
import java.util.ArrayList;

public class FCFS {
    // ---------------------------------------- Metoda wykonująca algorytm FCFS ----------------------------------------
    public static long[] execute(List<Request> requests) {
        requests.sort(null);  // Sortowanie po czasie przybycia

        long totalWaitingTime = 0;
        long maxWaitingTime = Long.MIN_VALUE;
        long minWaitingTime = Long.MAX_VALUE;
        long currentTime = 0;
        int currentCylinder = 0;
        long totalCylinderChanges = 0;
        int size = requests.size();

        List<Request> currentRequests = new ArrayList<>();  // Lista dostępnych żądań
        requests.sort(null);

        while (!requests.isEmpty()) {

            System.out.println(requests.size());
            if(currentTime<requests.get(0).getArrivalTime()){currentTime = requests.get(0).getArrivalTime();}

            for (Request req : requests) {
                if (req.getArrivalTime() <= currentTime) {
                    currentRequests.add(req);
                }
            }



            Request nextRequest = currentRequests.get(0);
            long waitingTime = currentTime - nextRequest.getArrivalTime();
            nextRequest.setWaitingTime(waitingTime);  // Ustawiamy czas oczekiwania
            totalWaitingTime += waitingTime;

            // Aktualizujemy max i min czas oczekiwania
            if (waitingTime > maxWaitingTime) {
                maxWaitingTime = waitingTime;
            }
            if (waitingTime < minWaitingTime) {
                minWaitingTime = waitingTime;
            }

            // Po obsłużeniu żądania, czas systemu jest zwiększany o czas realizacji operacji
            currentTime += Math.abs(nextRequest.getCylinder() - currentCylinder);  // Zwiększanie czasu o odległość do cylindra

            // Liczymy zmianę cylindra
            totalCylinderChanges += Math.abs(nextRequest.getCylinder() - currentCylinder);
            currentCylinder = nextRequest.getCylinder();  // Ustawiamy nową pozycję głowicy

            // Usuwamy przetworzone żądanie
            currentRequests.remove(nextRequest);
            requests.remove(nextRequest);  // Usuwamy żądanie z oryginalnej listy
        }

        long averageWaitingTime = totalWaitingTime / size;  // Obliczamy średni czas oczekiwania

        System.out.println("jd");
        return new long[] {maxWaitingTime, minWaitingTime, averageWaitingTime, totalCylinderChanges, 0};
    }
}
