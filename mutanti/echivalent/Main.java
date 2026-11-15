package ro.tss.armstrong;

public class Main {
    public static String evaluate(int n) {
        if ((n < 100 | n > 999)) {
            return "INVALID";
        }
        int rest = n;
        int suma = 0;
        while (rest > 0) {
            int cifra = rest % 10;
            suma += cifra * cifra * cifra;
            rest /= 10;
        }
        if (suma == n) {
            return "DA";
        }
        return "NU";
    }
}
