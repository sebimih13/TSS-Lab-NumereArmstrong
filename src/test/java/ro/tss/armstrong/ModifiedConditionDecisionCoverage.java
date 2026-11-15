package ro.tss.armstrong;

import org.junit.Test;
import static org.junit.Assert.assertEquals;

public class ModifiedConditionDecisionCoverage {
    @Test
    public void cazul_001() {
        assertEquals("NU", Main.evaluate(100));
    }

    @Test
    public void cazul_002() {
        assertEquals("DA", Main.evaluate(153));
    }

    @Test
    public void cazul_003() {
        assertEquals("INVALID", Main.evaluate(99));
    }
    
    @Test
    public void cazul_004() {
        assertEquals("INVALID", Main.evaluate(1000));
    }

}
