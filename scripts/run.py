"""Execută JUnit, JaCoCo, PIT și analizorul official Major, cu rapoarte persistente."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
TOOLS = Path(os.environ.get("TSS_TOOLS", ROOT / ".tools")).resolve()
SUITES = ["EpTest", "BvaTest", "CegTest", "McdcTest"]


def execute(args, log, cwd=ROOT, env=None, timeout=240, expected=0):
    log.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [str(a) for a in args],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    log.write_text(
        "$ " + " ".join(map(str, args)) + "\n" + proc.stdout, encoding="utf-8"
    )
    if proc.returncode != expected:
        raise RuntimeError(
            f"Cod {proc.returncode}, așteptat {expected}: {log}\n{proc.stdout[-3500:]}"
        )
    return proc.stdout


def java_home():
    override = os.environ.get("TSS_JAVA_HOME")
    return (
        Path(override) if override else Path(shutil.which("java")).resolve().parents[1]
    )


def deps():
    paths = [TOOLS / "junit-4.13.2.jar", TOOLS / "hamcrest-core-1.3.jar"]
    for p in paths:
        if not p.exists():
            raise RuntimeError(
                "Lipsește " + str(p) + "; verifică .tools/ sau TSS_TOOLS"
            )
    return paths


def compile_exercise(folder):
    reports = folder / "rapoarte"
    target = folder / "target"
    main = target / "classes"
    tests = target / "test-classes"
    # Curățăm numai output-ul compilatorului, niciodată sursele sau rapoartele.
    for p in [main, tests]:
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True)
    javac = java_home() / "bin/javac"
    execute(
        [
            javac,
            "-encoding",
            "UTF-8",
            "--release",
            "11",
            "-g",
            "-d",
            main,
            *sorted((folder / "src/main/java").rglob("*.java")),
        ],
        reports / "compile-main.log",
    )
    execute(
        [
            javac,
            "-encoding",
            "UTF-8",
            "--release",
            "11",
            "-g",
            "-cp",
            os.pathsep.join(map(str, [main, *deps()])),
            "-d",
            tests,
            *sorted((folder / "src/test/java").rglob("*.java")),
        ],
        reports / "compile-tests.log",
    )
    shutil.copytree(folder / "src/test/resources", tests, dirs_exist_ok=True)
    for dot in folder.glob("*.dot"):
        execute(
            ["dot", "-Tsvg", dot, "-o", dot.with_suffix(".svg")],
            reports / (dot.stem + "-render.log"),
        )
    return main, tests


def java_package(folder):
    return "ro.tss.armstrong"


def main_class(folder):
    return next((folder / "src/main/java").rglob("*.java")).stem


def class_name(folder, suite):
    aliases = {
        "EpTest": "EquivalencePartitioning",
        "BvaTest": "BoundaryValueAnalysis",
        "CegTest": "CauseEffectGraphing",
        "McdcTest": "ModifiedConditionDecisionCoverage",
    }
    name = aliases.get(suite, suite)
    return java_package(folder) + "." + name


def classpath(folder, main=None):
    return os.pathsep.join(
        map(
            str,
            [
                main or folder / "target/classes",
                folder / "target/test-classes",
                *deps(),
            ],
        )
    )


def junit(folder, suite, log, extra=(), main=None, expected=0):
    return execute(
        [
            java_home() / "bin/java",
            *extra,
            "-cp",
            classpath(folder, main),
            "org.junit.runner.JUnitCore",
            class_name(folder, suite),
        ],
        log,
        expected=expected,
    )


def tests(folder):
    result = {}
    for suite in SUITES + ["RegressionTest"]:
        output = junit(folder, suite, folder / "rapoarte/tests" / f"{suite}.log")
        m = re.search(r"OK \((\d+) tests?\)", output)
        if not m:
            raise RuntimeError("Lipsește confirmarea JUnit: " + suite)
        result[suite] = {"tests": int(m[1]), "passed": True}
    (folder / "rapoarte/tests.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def coverage(folder):
    result = {}
    for suite in SUITES + ["RegressionTest"]:
        p = folder / "rapoarte/coverage" / suite
        p.mkdir(parents=True, exist_ok=True)
        data = p / "jacoco.exec"
        junit(
            folder,
            suite,
            p / "junit.log",
            extra=[
                f"-javaagent:{TOOLS}/jacoco-agent-0.8.13.jar=destfile={data},append=false"
            ],
        )
        execute(
            [
                java_home() / "bin/java",
                "-jar",
                TOOLS / "jacoco-cli-0.8.13.jar",
                "report",
                data,
                "--classfiles",
                folder / "target/classes",
                "--sourcefiles",
                folder / "src/main/java",
                "--xml",
                p / "jacoco.xml",
                "--html",
                p / "html",
            ],
            p / "report.log",
        )
        xml = ET.parse(p / "jacoco.xml")
        method = xml.find('.//method[@name="evaluate"]')
        if method is None:
            raise RuntimeError("Raportul nu conține evaluate")
        result[suite] = {
            c.attrib["type"]: {
                "covered": int(c.attrib["covered"]),
                "missed": int(c.attrib["missed"]),
            }
            for c in method.findall("counter")
        }
    (folder / "rapoarte/coverage.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def manual(folder):
    selected, witness = (100,), (999,)
    p = folder / "target/manual"
    p.mkdir(parents=True, exist_ok=True)
    package = java_package(folder)
    for name, row in [("SelectedTest", selected), ("WitnessTest", witness)]:
        arguments = ", ".join(
            str(v).lower() if isinstance(v, bool) else str(v) for v in row
        )
        (p / (name + ".java")).write_text(
            f"package {package}; import org.junit.Test; import static org.junit.Assert.*; public class {name} {{ @Test public void rezultat() {{ assertEquals({json.dumps('NU')}, {main_class(folder)}.evaluate({arguments})); }} }}\n"
        )
    verify = p / "verify"
    verify.mkdir(exist_ok=True)
    execute(
        [
            java_home() / "bin/javac",
            "--release",
            "11",
            "-cp",
            classpath(folder),
            "-d",
            verify,
            p / "SelectedTest.java",
            p / "WitnessTest.java",
        ],
        folder / "rapoarte/manual/compile-tests.log",
    )
    results = {}
    for variant in ["original", "echivalent", "omorat", "supravietuitor"]:
        binary = folder / "target/classes" if variant == "original" else p / variant
        if variant != "original":
            binary.mkdir(exist_ok=True)
            execute(
                [
                    java_home() / "bin/javac",
                    "--release",
                    "11",
                    "-d",
                    binary,
                    folder / "mutanti" / variant / (main_class(folder) + ".java"),
                ],
                folder / "rapoarte/manual" / f"{variant}-compile.log",
            )
        cp = os.pathsep.join(
            map(str, [binary, verify, folder / "target/test-classes", *deps()])
        )
        outcomes = {}
        for name in ["SelectedTest", "WitnessTest"]:
            killed = (variant == "omorat" and name == "SelectedTest") or (
                variant == "supravietuitor" and name == "WitnessTest"
            )
            execute(
                [
                    java_home() / "bin/java",
                    "-cp",
                    cp,
                    "org.junit.runner.JUnitCore",
                    package + "." + name,
                ],
                folder / "rapoarte/manual" / f"{variant}-{name}.log",
                expected=1 if killed else 0,
            )
            outcomes[name] = "KILLED" if killed else "SAME_OUTPUT"
        if variant == "echivalent":
            execute(
                [
                    java_home() / "bin/java",
                    "-cp",
                    cp,
                    "org.junit.runner.JUnitCore",
                    *[class_name(folder, x) for x in SUITES + ["RegressionTest"]],
                ],
                folder / "rapoarte/manual/equivalent-full.log",
            )
        results[variant] = outcomes
    (folder / "rapoarte/manual.json").write_text(json.dumps(results, indent=2) + "\n")
    return results


def pit(folder):
    result = {}
    jars = [
        TOOLS / f"pitest{part}-1.17.4.jar" for part in ["", "-entry", "-command-line"]
    ]
    launcher = os.pathsep.join(
        map(
            str,
            [
                *jars,
                TOOLS / "commons-text-1.12.0.jar",
                TOOLS / "commons-lang3-3.14.0.jar",
                *deps(),
            ],
        )
    )
    for suite in SUITES:
        p = folder / "rapoarte/pit" / suite
        p.mkdir(parents=True, exist_ok=True)
        execute(
            [
                java_home() / "bin/java",
                "-cp",
                launcher,
                "org.pitest.mutationtest.commandline.MutationCoverageReport",
                "--reportDir",
                p,
                "--sourceDirs",
                folder / "src/main/java",
                "--targetClasses",
                class_name(folder, main_class(folder)),
                "--targetTests",
                class_name(folder, suite),
                "--classPath",
                ",".join(
                    map(
                        str,
                        [
                            folder / "target/classes",
                            folder / "target/test-classes",
                            *deps(),
                        ],
                    )
                ),
                "--mutableCodePaths",
                folder / "target/classes",
                "--excludedMethods",
                "<init>",
                "--outputFormats",
                "XML,HTML",
                "--timestampedReports",
                "false",
                "--threads",
                "2",
                "--timeoutConst",
                "1000",
                "--jvmPath",
                java_home() / "bin/java",
            ],
            p / "run.log",
        )
        counts = Counter(
            x.attrib["status"] for x in ET.parse(p / "mutations.xml").getroot()
        )
        operators = Counter(
            x.findtext("mutator") for x in ET.parse(p / "mutations.xml").getroot()
        )
        result[suite] = {
            "statuses": dict(counts),
            "operators": dict(operators),
            "total": sum(counts.values()),
        }
    (folder / "rapoarte/pit.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def jdk11():
    p = os.environ.get("TSS_JDK11")
    if p:
        return Path(p)
    found = list((TOOLS / "jdk11").glob("*/bin/javac"))
    if not found:
        raise RuntimeError(
            "Major necesită JDK11; setează TSS_JDK11 instalează JDK11 în .tools/jdk11/"
        )
    return found[0].parents[1]


def major(folder):
    result = {}
    base = folder / "rapoarte/major"
    base.mkdir(parents=True, exist_ok=True)
    binary = folder / "target/major-classes"
    binary.mkdir(parents=True, exist_ok=True)
    home = jdk11()
    env = dict(
        os.environ,
        PATH=str(home / "bin") + os.pathsep + os.environ["PATH"],
        JAVA_HOME=str(home),
    )
    execute(
        [
            TOOLS / "major/bin/major",
            "--mml",
            TOOLS / "major/mml/all.mml.bin",
            "--release",
            "11",
            "-g",
            "-d",
            binary,
            *sorted((folder / "src/main/java").rglob("*.java")),
        ],
        base / "compile.log",
        cwd=base,
        env=env,
    )
    log = base / "mutants.log"
    if not log.exists():
        raise RuntimeError("Major nu a produs mutants.log")
    for suite in SUITES:
        p = base / suite
        p.mkdir(parents=True, exist_ok=True)
        cp = [binary, folder / "target/test-classes", *deps()]
        xml = (
            '<project default="mutation"><target name="mutation"><junit mutationAnalysis="true" fork="false" printsummary="true" haltonfailure="true" excludeFailingTests="false" timeoutOffset="1000" mutantsLogFile="'
            + escape(str(log))
            + '" summaryFile="summary.csv" mutantDetailsFile="details.csv" exportKillMap="true" killMapFile="killMap.csv"><classpath>'
        )
        xml += "".join('<pathelement location="' + escape(str(x)) + '"/>' for x in cp)
        xml += (
            '</classpath><test name="'
            + class_name(folder, suite)
            + '"/></junit></target></project>'
        )
        build = p / "build.xml"
        build.write_text(xml)
        execute(
            [
                home / "bin/java",
                f"-Xbootclasspath/a:{TOOLS}/major/lib/major-rt.jar",
                "-jar",
                TOOLS / "major/lib/ant/ant-launcher.jar",
                "-f",
                build,
            ],
            p / "run.log",
            cwd=p,
            env=env,
            timeout=300,
        )
        # Formatul CSV este păstrat integral; parserul validează totalurile.
        with (p / "summary.csv").open() as f:
            summary = list(csv.DictReader(f))
        with (p / "details.csv").open() as f:
            details = list(csv.DictReader(f))
        result[suite] = {"summary": summary, "details_count": len(details)}
    (folder / "rapoarte/major.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def summary(folder):
    from analiza_mutatiilor import STATUS

    mutation = {}
    for tool in ["PIT", "Major"]:
        mutation[tool] = {}
        for suite in SUITES:
            if tool == "PIT":
                counts = Counter(
                    m.get("status")
                    for m in ET.parse(
                        folder / "rapoarte/pit" / suite / "mutations.xml"
                    ).getroot()
                )
            else:
                with (
                    folder / "rapoarte/major" / suite / "details.csv"
                ).open() as handle:
                    counts = Counter(
                        STATUS[row[1]] for row in list(csv.reader(handle))[1:]
                    )
            killed = counts["KILLED"] + counts["KILLED_EXCEPTION"]
            denominator = sum(counts.values()) - counts["TIMED_OUT"]
            mutation[tool][suite] = dict(
                killed=killed,
                denominator=denominator,
                percent=f"{100 * killed / denominator:.1f}%",
                statuses=dict(counts),
            )
    result = dict(
        exercise="armstrong",
        tests=json.loads((folder / "rapoarte/tests.json").read_text()),
        regression_inputs=len(
            (folder / "src/test/resources/regression.tsv").read_text().splitlines()
        ),
        coverage=json.loads((folder / "rapoarte/coverage.json").read_text()),
        mutation=mutation,
    )
    (folder / "rapoarte/rezumat.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=[
            "test",
            "coverage",
            "manual",
            "mutation",
            "pit",
            "major",
            "summary",
            "all",
        ],
    )
    args = parser.parse_args()
    folder = ROOT
    action = args.action
    if action != "summary":
        compile_exercise(folder)
    if action in ["test", "all"]:
        tests(folder)
    if action in ["coverage", "all"]:
        coverage(folder)
    if action in ["manual", "all"]:
        manual(folder)
    if action in ["mutation", "pit", "all"]:
        pit(folder)
    if action in ["mutation", "major", "all"]:
        major(folder)
    if action in ["summary", "all"]:
        summary(folder)
    if action == "all":
        from analiza_mutatiilor import main as analyze

        analyze()
    print("Armstrong", action, "OK", flush=True)


if __name__ == "__main__":
    main()
