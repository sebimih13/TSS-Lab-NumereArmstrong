package ro.tss.armstrong;

import org.junit.Test;
import static org.junit.Assert.assertEquals;

public class EquivalncePartitioning {
    @Test
    public void EP01() {
        assertEquals("DA", Main.evaluate(153));
    }

    @Test
    public void EP02() {
        assertEquals("NU", Main.evaluate(123));
    }

    @Test
    public void EP03() {
        assertEquals("INVALID", Main.evaluate(99));
    }

    @Test
    public void EP04() {
        assertEquals("INVALID", Main.evaluate(1000));
    }

}
