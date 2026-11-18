package ro.tss.armstrong;

import org.junit.Test;
import static org.junit.Assert.*;
import java.io.*;
import java.nio.charset.StandardCharsets;

public class RegressionTest {
    @Test
    public void verificaMatriceaIndependenta() throws Exception {
        int count = 0;
        try (BufferedReader r = new BufferedReader(new InputStreamReader(
                getClass().getResourceAsStream("/regression.tsv"), StandardCharsets.UTF_8))) {
            String line;
            while ((line = r.readLine()) != null) {
                String[] p = line.split("\t");
                assertEquals("Linia " + (count + 1) + ": " + line, p[1], Main.evaluate(Integer.parseInt(p[0])));
                count++;
            }
        }
        assertEquals(902, count);
    }

}
