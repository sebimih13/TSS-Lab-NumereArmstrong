package ro.tss.armstrong;
import org.junit.Test;
import static org.junit.Assert.assertEquals;
public class BoundaryValueAnalysis {
    @Test
    public void BVA01() {
        assertEquals("INVALID", Main.evaluate(99));
    }

    @Test
    public void BVA02() {
        assertEquals("NU", Main.evaluate(100));
    }

    @Test
    public void BVA03() {
        assertEquals("NU", Main.evaluate(101));
    }

    @Test
    public void BVA04() {
        assertEquals("NU", Main.evaluate(152));
    }

    @Test
    public void BVA05() {
        assertEquals("DA", Main.evaluate(153));
    }

    @Test
    public void BVA06() {
        assertEquals("NU", Main.evaluate(154));
    }

    @Test
    public void BVA07() {
        assertEquals("NU", Main.evaluate(369));
    }

    @Test
    public void BVA08() {
        assertEquals("DA", Main.evaluate(370));
    }

    @Test
    public void BVA09() {
        assertEquals("DA", Main.evaluate(371));
    }

    @Test
    public void BVA10() {
        assertEquals("NU", Main.evaluate(372));
    }

    @Test
    public void BVA11() {
        assertEquals("NU", Main.evaluate(406));
    }

    @Test
    public void BVA12() {
        assertEquals("DA", Main.evaluate(407));
    }

    @Test
    public void BVA13() {
        assertEquals("NU", Main.evaluate(408));
    }

    @Test
    public void BVA14() {
        assertEquals("NU", Main.evaluate(998));
    }

    @Test
    public void BVA15() {
        assertEquals("NU", Main.evaluate(999));
    }

    @Test
    public void BVA16() {
        assertEquals("INVALID", Main.evaluate(1000));
    }

}
