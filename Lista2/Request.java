import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Request implements Comparable
{
    ///POLA KLASY
    /***
     * cylinder - numer potrzebnego cylindra
     * arrivalTime - czas w którym dane żądanie przybyło
     * deadline - jest potrzebny przy EDF (czas do któego żądanie musi zostać wykonane)
     * priority - dla czasu rzeczywistego priorytet danego requesta
     * waitingTime - czas oczekiwania dla danego requesta (przydatny do dalszej analizy)
     * status - status żądania, ważny kiedy mamy liste żądań , i mamy oczekujące lub obecne
     */
    // ---------------------------------------- Pola klasy ----------------------------------------
    private int cylinder;         // Numer cylindra
    private long arrivalTime;     // Czas zgłoszenia (dla FCFS)
    private long deadline;        // Deadline (dla EDF)
    private int priority;         // Priorytet (dla aplikacji czasu rzeczywistego)
    private long waitingTime;     // Czas oczekiwania
    private String status;        // Status żądania ('waiting', 'in_progress', 'completed')
    // ----------------------------------------------------------------------------------------

    ///KONSTRUKTOR
    // ---------------------------------------- Konstruktor ----------------------------------------
    public Request(int cylinder, long arrivalTime, long deadline, int priority) {
        this.cylinder = cylinder;
        this.arrivalTime = arrivalTime;
        this.deadline = deadline;
        this.priority = priority;
        this.waitingTime = 0;
        this.status = "waiting";
    }
    // ---------------------------------------------------------------------------------------------

    /// CompareTo
    // ---------------------------------------------------------------------------------------------
    public int compareTo(Object T)
    {
        if(((Request)T).arrivalTime >this.arrivalTime) return -1;
        return 1;
    }
    // ---------------------------------------------------------------------------------------------

    ///GETTERY I SETTERY (ONE SĄ WYGENEROWANE, WIĘC NIEKTÓRE NIE SĄ UŻYWANE)
    // ---------------------------------------- Gettery i Settery ----------------------------------------
    public int getCylinder() {
        return cylinder;
    }

    public void setCylinder(int cylinder) {
        this.cylinder = cylinder;
    }

    public long getArrivalTime() {
        return arrivalTime;
    }

    public void setArrivalTime(long arrivalTime) {
        this.arrivalTime = arrivalTime;
    }

    public long getDeadline() {
        return deadline;
    }

    public void setDeadline(long deadline) {
        this.deadline = deadline;
    }

    public int getPriority() {
        return priority;
    }

    public void setPriority(int priority) {
        this.priority = priority;
    }

    public long getWaitingTime() {
        return waitingTime;
    }

    public void setWaitingTime(long waitingTime) {
        this.waitingTime = waitingTime;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
    // ----------------------------------------------------------------------------------------

    // ---------------------------------------- Statyczna metoda generująca n żądań ----------------------------------------
    public static List<Request> generateRequests(int n, int minCylinder, int maxCylinder, long minArrivalTime, long maxArrivalTime, long minDeadline, long maxDeadline) {
        Random rand = new Random();
        List<Request> requests = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            // Losowanie cylindra (losuje pozycje cylindra dla żądania)
            int cylinder = rand.nextInt(maxCylinder - minCylinder + 1) + minCylinder;

            // Losowanie czasu zgłoszenia (arrivalTime) w zakresie podanym w zadaniu (kiedy dane żądanie doszło, to jest potrzebne , gdy mamy dla czasu rzeczywistego algorytmy)
            long arrivalTime = minArrivalTime + (long)(rand.nextDouble() * (maxArrivalTime - minArrivalTime));

            // Losowanie deadline (jeśli ma być stosowane w EDF) (deadliney oczywiste zastosowanie dla EDF)
            long deadline = minDeadline + (long)(rand.nextDouble() * (maxDeadline - minDeadline));

            // Losowanie priorytetu (jeśli dotyczy) ()
            int priority = rand.nextInt(2);  // Przykład: 0 - niski priorytet, 1 - wysoki priorytet

            // Losowanie typu żądania (np. 'read' lub 'write')
            String requestType = rand.nextBoolean() ? "read" : "write";

            // Losowanie ID dysku (jeśli system ma więcej niż jeden dysk)
            int diskId = rand.nextInt(3);  // Zakładając 3 dyski (0, 1, 2)

            // Tworzenie nowego żądania i dodanie do listy
            requests.add(new Request(cylinder, arrivalTime, deadline, priority));
        }

        return requests;
    }
    // ----------------------------------------------------------------------------------------


    // ---------------------------------------- Reprezentacja tekstowa obiektu (dla debugowania) ----------------------------------------
    @Override
    public String toString() {
        return "Request{" +
                "cylinder=" + cylinder +
                ", arrivalTime=" + arrivalTime +
                ", deadline=" + deadline +
                ", priority=" + priority +
                ", waitingTime=" + waitingTime +
                ", status='" + status + '\'' +
                '}';
    }
    // ----------------------------------------------------------------------------------------
}
