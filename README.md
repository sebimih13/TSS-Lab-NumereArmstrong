# TSS-Lab-NumereArmstrong
## Requirements înainte de rulare

- Bash
- Python 3.10+; numai biblioteca standard, fără pachete `pip`.
- JDK 17 cu `java` în `PATH`; runnerul folosește `javac` din același JDK și compilează cu `--release 11`.
- Graphviz (`dot` în `PATH`), folosit la recompilarea grafului.
- Fișiere existente în `main/.tools/`:
  - `junit-4.13.2.jar`
  - `hamcrest-core-1.3.jar`
  - `jacoco-agent-0.8.13.jar`
  - `jacoco-cli-0.8.13.jar`
  - `pitest-1.17.4.jar`
  - `pitest-entry-1.17.4.jar`
  - `pitest-command-line-1.17.4.jar`
  - `commons-text-1.12.0.jar`
  - `commons-lang3-3.14.0.jar`
- Major 3.0.1 instalat în `main/.tools/major/`, inclusiv runtime-ul și Ant.
- JDK 11 instalat în `main/.tools/jdk11/*/`, necesar pentru Major.
- Sursele din `src/main/java/`, testele din `src/test/java/` și fișierul `src/test/resources/regression.tsv`.

## Comenzi folosite

```bash
cd /home/seb/Developer/TSS-Lab-Proiect

python3 --version
java -version
javac -version
dot -V

# Recompilare și rulare JUnit: EP, BVA, CEG, MC/DC, RegressionTest.
# Rezultate: main/14_armstrong/rapoarte/tests/ și rapoarte/tests.json.
python3 main/tools/run.py test --exercise 14_armstrong

# Recompilare, rulare JUnit cu agentul JaCoCo și generare HTML/XML.
# Fiecare suită rulează într-un JVM separat, cu append=false.
# Rezultate: main/14_armstrong/rapoarte/coverage/ și rapoarte/coverage.json.
python3 main/tools/run.py coverage --exercise 14_armstrong

# Toate rapoartele: JUnit, JaCoCo, mutanți manuali, PIT și Major.
python3 main/tools/run.py all --exercise 14_armstrong

# Rerulare separată PIT și Major.
python3 main/tools/run.py mutation --exercise 14_armstrong

# Validare PIT/Major, recalculare tabele LaTeX și verificare martori Java.
python3 main/14_armstrong/scripts/analiza_mutatiilor.py

# Regenerare REZULTATE.md și rapoarte/rezumat.json doar pentru Armstrong.
PYTHONPATH=main/tools python3 -c 'import report; report.main({"14_armstrong"})'
```
