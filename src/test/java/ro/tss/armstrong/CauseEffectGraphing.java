package ro.tss.armstrong;
import org.junit.Test;
import static org.junit.Assert.assertEquals;
public class CauseEffectGraphing {
    @Test
    public void CEG01() {
        assertEquals("INVALID", Main.evaluate(99));
    }

    @Test
    public void CEG02() {
        assertEquals("NU", Main.evaluate(100));
    }

    @Test
    public void CEG03() {
        assertEquals("DA", Main.evaluate(153));
    }

}
