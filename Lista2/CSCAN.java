import java.util.List;

public class CSCAN {
    public static long[] execute(List<Request> requests) {
        if (requests.isEmpty()) {
            return new long[] {0, 0, 0, 0, 0}; // Zwracamy 0, jeśli nie ma żądań
        }

        long totalWaitingTime = 0;
        long maxWaitingTime = Long.MIN_VALUE;
        long minWaitingTime = Long.MAX_VALUE;

        int currentCylinder = 0;
        long totalCylinderChanges = 0;

        long currentTime = 0;

        while (!requests.isEmpty()) {
            requests.sort(null);
            System.out.println(requests.size());
            if(currentTime<requests.get(0).getArrivalTime()){currentTime = requests.get(0).getArrivalTime();}

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

            if (currentCylinder == 180) {
                currentCylinder = 0;
                totalCylinderChanges += 180;
            }

            requests.remove(0);
        }

        long averageWaitingTime = (requests.isEmpty()) ? 0 : totalWaitingTime / requests.size();

        return new long[] {maxWaitingTime, minWaitingTime, averageWaitingTime, totalCylinderChanges, 0};
    }
}
