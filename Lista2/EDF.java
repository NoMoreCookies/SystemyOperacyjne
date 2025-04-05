import java.util.List;

public class EDF {
    public static long[] execute(List<Request> requests) {
        if (requests.isEmpty()) {
            return new long[] {0, 0, 0, 0, 0}; // Zwracamy 0, jeśli nie ma żądań
        }

        // Sortowanie żądań po czasie przybycia
        requests.sort((r1, r2) -> Long.compare(r1.getArrivalTime(), r2.getArrivalTime()));

        long totalWaitingTime = 0;
        long maxWaitingTime = Long.MIN_VALUE;
        long minWaitingTime = Long.MAX_VALUE;

        int currentCylinder = 0;
        long totalCylinderChanges = 0;

        long currentTime = 0;

        while (!requests.isEmpty()) {
            // Sortowanie według deadline (earliest deadline first)
            requests.sort((r1, r2) -> Long.compare(r1.getDeadline(), r2.getDeadline()));

            Request closestRequest = requests.get(0);

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
        }

        long averageWaitingTime = (requests.isEmpty()) ? 0 : totalWaitingTime / requests.size();
        return new long[] {maxWaitingTime, minWaitingTime, averageWaitingTime, totalCylinderChanges, 0};
    }
}
