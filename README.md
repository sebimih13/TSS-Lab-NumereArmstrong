# TSS-Lab-NumereArmstrong

Comenzile se rulează din rădăcina acestui repository. Numele directorului nu influențează pachetul Java sau selecția suitelor.

## Cerințe

- Bash și Python 3.10+ (numai biblioteca standard).
- JDK 17 cu `java` în `PATH`; compilarea folosește `--release 11`.
- Pentru PDF: TeX Live cu pachetele din `main.tex` și `latexmk`.
- Maven (`mvn`) și acces la Maven Central la prima rulare.

`pom.xml` descarcă automat următoarele JAR-uri în `.tools/` la `mvn generate-test-resources` sau `mvn test`, pentru a putea fi folosite și de scripturile Python:

  - `junit-4.13.2.jar`, `hamcrest-core-1.3.jar`
  - `jacoco-agent-0.8.13.jar`, `jacoco-cli-0.8.13.jar`
  - `pitest-1.17.4.jar`, `pitest-entry-1.17.4.jar`, `pitest-command-line-1.17.4.jar`
  - `commons-text-1.12.0.jar`, `commons-lang3-3.14.0.jar`

Pentru analiza Major și `python3 scripts/run.py all`, instalează separat:

- Major 3.0.1 în `.tools/major/`, inclusiv runtime-ul și Ant.
- JDK 11 în `.tools/jdk11/*/`; alternativ, `TSS_JDK11` indică rădăcina JDK-ului.

JDK-urile, Maven și distribuția Major nu sunt instalate de `pom.xml`. Python este necesar pentru scripturi, iar TeX Live și `latexmk` doar pentru PDF.

Uneltele binare nu sunt incluse în Git. Poți reutiliza instalarea existentă din proiectul inițial:

```bash
devbox run setup
```

## Generare

```bash
# Pregătirea JAR-urilor pentru scripturi (o singură dată).
devbox run prepare

# JUnit, JaCoCo, mutanți manuali, PIT, Major, rezumat și analiza mutațiilor.
devbox run run

# Rulări separate.
devbox run run test
devbox run run coverage
devbox run run manual
devbox run run mutation
# Sunt disponibile și acțiunile pit și major.

# Refacerea rezumatului din rapoartele deja generate.
devbox run run summary

# Validare PIT/Major, tabele LaTeX și martori Java.
devbox run validate

# PDF, inclusiv graful TikZ și tabelele generate.
devbox run pdf

# Alternativă pentru testele și raportul JaCoCo prin Maven.
devbox run test

# Verificarea runnerului fără unelte Java.
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Rezultatele se scriu în `rapoarte/`: `tests/`, `coverage/` (HTML/XML), `manual/`, `pit/` (HTML/XML), `major/`, `studiu_mutatie/`, fișierele JSON și `rezumat.json`. PDF-ul se scrie în `main.pdf`. Imaginile de acoperire din `figuri/` sunt capturi statice; rapoartele HTML actualizate sunt în `rapoarte/coverage/`.

PIT folosește socket-uri locale pentru comunicarea cu procesele JVM; mediul de execuție trebuie să le permită.
