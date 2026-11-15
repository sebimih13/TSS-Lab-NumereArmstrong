# TSS-Lab-NumereArmstrong

Comenzile se rulează din rădăcina acestui repository. Numele directorului nu influențează pachetul Java sau selecția suitelor.

## Cerințe

- Bash și Python 3.10+ (numai biblioteca standard).
- JDK 17 cu `java` în `PATH`; compilarea folosește `--release 11`.
- Pentru PDF: TeX Live cu pachetele din `main.tex` și `latexmk`.
- Pentru Maven: `mvn` și acces la Maven Central la prima rulare.
- Uneltele de testare în `.tools/` sau într-un director indicat prin `TSS_TOOLS`:
  - `junit-4.13.2.jar`, `hamcrest-core-1.3.jar`
  - `jacoco-agent-0.8.13.jar`, `jacoco-cli-0.8.13.jar`
  - `pitest-1.17.4.jar`, `pitest-entry-1.17.4.jar`, `pitest-command-line-1.17.4.jar`
  - `commons-text-1.12.0.jar`, `commons-lang3-3.14.0.jar`
  - Major 3.0.1 în `major/`, inclusiv runtime-ul și Ant.
  - JDK 11 în `jdk11/*/`, necesar pentru Major; alternativ, `TSS_JDK11` indică rădăcina JDK-ului.

Uneltele binare nu sunt incluse în Git. Poți reutiliza instalarea existentă din proiectul inițial:

```bash
export TSS_TOOLS=/home/seb/Developer/TSS-Lab-Proiect/main/.tools
```

## Generare

```bash
# JUnit, JaCoCo, mutanți manuali, PIT, Major, rezumat și analiza mutațiilor.
python3 scripts/run.py all

# Rulări separate.
python3 scripts/run.py test
python3 scripts/run.py coverage
python3 scripts/run.py manual
python3 scripts/run.py mutation
# Sunt disponibile și acțiunile pit și major.

# Refacerea rezumatului din rapoartele deja generate.
python3 scripts/run.py summary

# Validare PIT/Major, tabele LaTeX și martori Java.
python3 scripts/analiza_mutatiilor.py

# PDF, inclusiv graful TikZ și tabelele generate.
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

# Alternativă pentru testele și raportul JaCoCo prin Maven.
mvn test

# Verificarea runnerului fără unelte Java.
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Rezultatele se scriu în `rapoarte/`: `tests/`, `coverage/` (HTML/XML), `manual/`, `pit/` (HTML/XML), `major/`, `studiu_mutatie/`, fișierele JSON și `rezumat.json`. PDF-ul se scrie în `main.pdf`. Imaginile de acoperire din `figuri/` sunt capturi statice; rapoartele HTML actualizate sunt în `rapoarte/coverage/`.

PIT folosește socket-uri locale pentru comunicarea cu procesele JVM; mediul de execuție trebuie să le permită.
