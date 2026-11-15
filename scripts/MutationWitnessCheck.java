import major.mutation.Config;
import ro.tss.armstrong.Main;

/** Verifies concrete witnesses against Major's compiled mutants. */
public class MutationWitnessCheck {
    private static String evaluate(int mutant, int n) {
        Config.__M_NO = mutant;
        return Main.evaluate(n);
    }

    private static void witness(int mutant, int n, String expectedOriginal,
                                String expectedMutant) {
        String original = evaluate(0, n);
        String changed = evaluate(mutant, n);
        if (!expectedOriginal.equals(original) || !expectedMutant.equals(changed)) {
            throw new AssertionError("Unexpected result for mutant " + mutant + ", n=" + n);
        }
        System.out.println("WITNESS " + mutant + " " + n + " " + original + " " + changed);
    }

    public static void main(String[] args) {
        witness(2, 100, "NU", "INVALID");
        witness(5, 999, "NU", "INVALID");
        witness(6, 1000, "INVALID", "NU");
        witness(7, 1000, "INVALID", "NU");
        witness(29, 154, "NU", "DA");
        int checks = 0;
        for (int n = 100; n <= 999; n++) {
            if (!evaluate(0, n).equals(evaluate(11, n))) {
                throw new AssertionError("Mutant 11 differs for n=" + n);
            }
            checks++;
        }
        int[] invalid = {Integer.MIN_VALUE, -1, 0, 99, 1000, Integer.MAX_VALUE};
        for (int n : invalid) {
            if (!evaluate(0, n).equals(evaluate(11, n))) {
                throw new AssertionError("Mutant 11 differs for n=" + n);
            }
            checks++;
        }
        Config.__M_NO = 0;
        System.out.println("EQUIVALENT_11_CHECKS " + checks);
    }
}
