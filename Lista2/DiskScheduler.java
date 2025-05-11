import java.util.List;
import java.util.ArrayList;

public class DiskScheduler {
    public static void main(String[] args) {
        // ---------------------------------------- Generowanie 10 żądań (6 zestawów danych) ----------------------------------------
        int numTrials = 10;  // Liczba prób dla każdego algorytmu

        // Zmienna do przechowywania wyników dla każdego algorytmu
        List<List<Long>> fcfsResults = new ArrayList<>();
        List<List<Long>> sstfResults = new ArrayList<>();
        List<List<Long>> scanResults = new ArrayList<>();
        List<List<Long>> cscanResults = new ArrayList<>();
        List<List<Long>> edfResults = new ArrayList<>();
        List<List<Long>> fdscanResults = new ArrayList<>();
        // ------------------------------------------------------------------------------------------------------------------

        // ---------------------------------------- Przeprowadzenie 10 prób dla każdego algorytmu ----------------------------------------
        for (int i = 0; i < numTrials; i++) {
            // Generowanie różnych zestawów danych dla każdej próby
            List<Request> requestsFCFS = Request.generateRequests(10, 0, 180, 0, 100, 50, 150);

            // Tworzenie kopii listy żądań, aby operować na różnych kopiach
            List<Request> requestsSSTF = new ArrayList<>(requestsFCFS);
            List<Request> requestsSCAN = new ArrayList<>(requestsFCFS);
            List<Request> requestsCSCAN = new ArrayList<>(requestsFCFS);
            List<Request> requestsEDF = new ArrayList<>(requestsFCFS);
            List<Request> requestsFDSCAN = new ArrayList<>(requestsFCFS);

            // Wywołanie algorytmu FCFS i zapisanie wyników
            long[] resultsFCFS = FCFS.execute(new ArrayList<>(requestsFCFS));  // Przekazywanie kopii listy
            fcfsResults.add(toList(resultsFCFS));  // Dodanie wyników FCFS do listy

            // Wywołanie algorytmu SSTF i zapisanie wyników
            long[] resultsSSTF = SSTF.execute(new ArrayList<>(requestsSSTF));  // Przekazywanie kopii listy
            sstfResults.add(toList(resultsSSTF));  // Dodanie wyników SSTF do listy

            // Wywołanie algorytmu SCAN i zapisanie wyników
            long[] resultsSCAN = SCAN.execute(new ArrayList<>(requestsSCAN));  // Przekazywanie kopii listy
            scanResults.add(toList(resultsSCAN));  // Dodanie wyników SCAN do listy

            // Wywołanie algorytmu C-SCAN i zapisanie wyników
            //long[] resultsCSCAN = CSCAN.execute(new ArrayList<>(requestsCSCAN));  // Przekazywanie kopii listy
            //cscanResults.add(toList(resultsCSCAN));  // Dodanie wyników C-SCAN do listy

            // Wywołanie algorytmu EDF i zapisanie wyników
            //long[] resultsEDF = EDF.execute(new ArrayList<>(requestsEDF));  // Przekazywanie kopii listy
            //edfResults.add(toList(resultsEDF));  // Dodanie wyników EDF do listy

            // Wywołanie algorytmu FD-SCAN i zapisanie wyników
            //long[] resultsFDSCAN = FDSCAN.execute(new ArrayList<>(requestsFDSCAN));  // Przekazywanie kopii listy
            //fdscanResults.add(toList(resultsFDSCAN));  // Dodanie wyników FD-SCAN do listy
        }
        // ------------------------------------------------------------------------------------------------------------------

        // ---------------------------------------- Obliczanie średnich, odchyleń standardowych, wariancji oraz max/min dla każdego algorytmu ----------------------------------------
        System.out.println("FCFS Statistics:");
        printStatistics(fcfsResults);  // Obliczanie i wyświetlanie wyników FCFS

        System.out.println("\nSSTF Statistics:");
        printStatistics(sstfResults);  // Obliczanie i wyświetlanie wyników SSTF

        System.out.println("\nSCAN Statistics:");
        printStatistics(scanResults);  // Obliczanie i wyświetlanie wyników SCAN

        System.out.println("\nC-SCAN Statistics:");
        //printStatistics(cscanResults);  // Obliczanie i wyświetlanie wyników C-SCAN

        System.out.println("\nEDF Statistics:");
        //printStatistics(edfResults);  // Obliczanie i wyświetlanie wyników EDF

        System.out.println("\nFD-SCAN Statistics:");
        //printStatistics(fdscanResults);  // Obliczanie i wyświetlanie wyników FD-SCAN
        // ------------------------------------------------------------------------------------------------------------------
    }

    // ---------------------------------------- Pomocnicza metoda konwertująca tablicę na listę ----------------------------------------
    private static List<Long> toList(long[] array) {
        List<Long> list = new ArrayList<>();
        for (long value : array) {  // Iterujemy po tablicy i dodajemy elementy do listy
            list.add(value);
        }
        return list;  // Zwracamy listę
    }
    // ------------------------------------------------------------------------------------------------------------------

    // ---------------------------------------- Funkcja pomocnicza do obliczania średnich, odchyleń standardowych, wariancji, max i min ----------------------------------------
    private static void printStatistics(List<List<Long>> results) {
        long totalMaxWaitingTime = 0;  // Zmienna do sumowania maksymalnych czasów oczekiwania
        long totalWaitingTime = 0;  // Zmienna do sumowania czasów oczekiwania
        long totalCylinderChanges = 0;  // Zmienna do sumowania zmian cylindra
        long[] allMaxTimes = new long[results.size()];  // Tablica do przechowywania maksymalnych czasów oczekiwania
        long[] allAverageTimes = new long[results.size()];  // Tablica do przechowywania średnich czasów oczekiwania

        // Iterujemy po wszystkich próbach, aby obliczyć wartości
        for (int i = 0; i < results.size(); i++) {
            List<Long> result = results.get(i);  // Pobieramy wyniki z i-tej próby
            long maxWaitingTime = result.get(0);  // Maksymalny czas oczekiwania
            long averageWaitingTime = result.get(2);  // Średni czas oczekiwania
            long cylinderChanges = result.get(3);  // Zmiany cylindra

            totalMaxWaitingTime += maxWaitingTime;  // Sumujemy maksymalne czasy oczekiwania
            totalWaitingTime += averageWaitingTime;  // Sumujemy średnie czasy oczekiwania
            totalCylinderChanges += cylinderChanges;  // Sumujemy zmiany cylindra

            allMaxTimes[i] = maxWaitingTime;  // Dodajemy wynik do tablicy maxWaitingTime
            allAverageTimes[i] = averageWaitingTime;  // Dodajemy wynik do tablicy averageWaitingTime
        }

        // Obliczanie średnich
        long averageMaxWaitingTime = totalMaxWaitingTime / results.size();  // Średnia maksymalnych czasów oczekiwania
        long averageAvgWaitingTime = totalWaitingTime / results.size();  // Średnia średnich czasów oczekiwania
        long averageCylinderChanges = totalCylinderChanges / results.size();  // Średnia liczby zmian cylindra

        // Obliczanie odchylenia standardowego i wariancji
        double varianceMaxWaitingTime = 0;  // Zmienna do obliczania wariancji dla maxWaitingTime
        double varianceAvgWaitingTime = 0;  // Zmienna do obliczania wariancji dla averageWaitingTime
        for (int i = 0; i < results.size(); i++) {
            varianceMaxWaitingTime += Math.pow(allMaxTimes[i] - averageMaxWaitingTime, 2);  // Obliczanie wariancji
            varianceAvgWaitingTime += Math.pow(allAverageTimes[i] - averageAvgWaitingTime, 2);  // Obliczanie wariancji
        }
        varianceMaxWaitingTime /= results.size();  // Obliczanie średniej wariancji
        varianceAvgWaitingTime /= results.size();  // Obliczanie średniej wariancji

        double stdDevMaxWaitingTime = Math.sqrt(varianceMaxWaitingTime);  // Odchylenie standardowe dla maxWaitingTime
        double stdDevAvgWaitingTime = Math.sqrt(varianceAvgWaitingTime);  // Odchylenie standardowe dla averageWaitingTime

        // Wypisanie wyników
        System.out.println("Average Max Waiting Time: " + averageMaxWaitingTime);
        System.out.println("Average Waiting Time: " + averageAvgWaitingTime);
        System.out.println("Average Cylinder Changes (Distance): " + averageCylinderChanges);
        System.out.println("Standard Deviation Max Waiting Time: " + stdDevMaxWaitingTime);
        System.out.println("Standard Deviation Average Waiting Time: " + stdDevAvgWaitingTime);
        System.out.println("Max Cylinder Changes (Distance): " + findMax(allMaxTimes));
    }

    // Funkcja pomocnicza do znajdowania maksymalnej wartości w tablicy
    private static long findMax(long[] array) {
        long max = array[0];  // Inicjalizacja zmiennej do przechowywania maksymalnej wartości
        for (long val : array) {  // Iterujemy po tablicy
            if (val > max) {
                max = val;  // Jeśli napotkamy większą wartość, ustawiamy ją jako nowy max
            }
        }
        return max;  // Zwracamy maksymalną wartość
    }
}
