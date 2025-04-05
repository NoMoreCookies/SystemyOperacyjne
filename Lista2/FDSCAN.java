import java.util.List;

public class FDSCAN {
    public static long[] execute(List<Request> requests) {
        if (requests.isEmpty()) {
            return new long[] {0, 0, 0, 0, 0}; // Zwracamy 0, jeśli nie ma żądań
        }

        // Sortowanie po czasie przybycia
        requests.sort((r1, r2) -> Long.compare(r1.getArrivalTime(), r2.getArrivalTime()));

        long totalWaitingTime = 0;
        long maxWaitingTime = Long.MIN_VALUE;
        long minWaitingTime = Long.MAX_VALUE;

        int currentCylinder = 0;
        long totalCylinderChanges = 0;

        long currentTime = 0;

        while (!requests.isEmpty()) {
            // Sortowanie według czasu przybycia (FCFS)
            requests.sort((r1, r2) -> Long.compare(r1.getArrivalTime(), r2.getArrivalTime()));

            Request closestRequest = requests.get(0);

            // Sprawdzamy, czy żądanie mieści się w czasie
            if (currentTime <= closestRequest.getDeadline()) {
                currentTime = Math.max(currentTime, closestRequest.getArrivalTime());

                long waitingTime = currentTime - closestRequest.getArrivalTime();
                closestRequest.setWaitingTime(waitingTime);
                totalWaitingTime += waitingTime;

                if (waitingTime > maxWaitingTime) maxWaitingTime = waitingTime;
                if (waitingTime < minWaitingTime) minWaitingTime = waitingTime;

                currentTime += 1;
                totalCylinderChanges += Math.abs(closestRequest.getCylinder() - currentCylinder);
                currentCylinder = closestRequest.getCylinder();

                requests.remove(closestRequest);
            } else {
                requests.remove(closestRequest); // Usuwamy żądanie, które nie spełnia warunków
            }
        }

        long averageWaitingTime = (requests.isEmpty()) ? 0 : totalWaitingTime / requests.size();
        return new long[] {maxWaitingTime, minWaitingTime, averageWaitingTime, totalCylinderChanges, 0};
    }
}
