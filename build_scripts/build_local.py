#!/usr/bin/env python3
"""Build Tickets Hunter locally and check the result is actually runnable.

PyInstaller cannot cross-compile: the frozen bundle carries this machine's
Python runtime and the compiled extensions that came with it (onnxruntime
behind ddddocr, cryptography). A Windows run produces only a Windows build and
a macOS run only a macOS build, so verifying both platforms means running this
on both.

This deliberately does less than build_and_test.bat, which installs
dependencies, packages a ZIP, runs the test suite and writes a report. The job
here is the one question that script buries: does PyInstaller produce a bundle
that starts? That is what the spec file's excludes and every native dependency
upgrade can silently break, and it is worth being able to re-run in under a
minute.

    python build_scripts/build_local.py            build, assemble, verify
    python build_scripts/build_local.py --skip-build   re-verify an existing dist
    python build_scripts/build_local.py --keep         leave build/ for inspection

Exit code is 0 only when every check passes.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD_SCRIPTS = ROOT / "build_scripts"
DIST = ROOT / "dist"
STAGE = DIST / "tickets_hunter"

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
EXE_SUFFIX = ".exe" if IS_WINDOWS else ""

SPECS = ["nodriver_tixcraft", "settings"]

# The bot's own help screen is the smoke test. nodriver_tixcraft.py imports
# every platform module at module level, and those pull in zendriver and
# ddddocr, so argparse printing usage means the whole import chain unpacked and
# loaded inside the frozen bundle. Anything less only proves the file exists.
SMOKE_TIMEOUT = 120

results = []


def step(name, ok, detail=""):
    results.append((name, ok, detail))
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail else ""))
    return ok


def run(cmd, **kwargs):
    print(f"    $ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, cwd=ROOT, **kwargs)


def preflight():
    print("\n[1/5] Preflight")
    step("python >= 3.10", sys.version_info >= (3, 10),
         f"running {sys.version.split()[0]}")

    proc = run([sys.executable, "-m", "PyInstaller", "--version"],
               capture_output=True, text=True)
    if proc.returncode != 0:
        return step("PyInstaller installed", False,
                    "pip install pyinstaller")
    step("PyInstaller installed", True, proc.stdout.strip())

    missing = []
    for mod in ("ddddocr", "zendriver", "tornado", "cryptography"):
        probe = run([sys.executable, "-c", f"import {mod}"],
                    capture_output=True, text=True)
        if probe.returncode != 0:
            missing.append(mod)
    return step("core imports work in this interpreter", not missing,
                f"missing: {', '.join(missing)}" if missing else
                "ddddocr, zendriver, tornado, cryptography")


def build():
    print("\n[2/5] PyInstaller")
    # A stale dist/ is the classic way to "verify" a build that never ran, so
    # it goes before anything else rather than after a failure.
    for path in (DIST, ROOT / "build"):
        if path.exists():
            shutil.rmtree(path)

    for name in SPECS:
        started = time.time()
        proc = run([sys.executable, "-m", "PyInstaller",
                    str(BUILD_SCRIPTS / f"{name}.spec"),
                    "--clean", "--noconfirm"])
        if not step(f"build {name}", proc.returncode == 0,
                    f"{time.time() - started:.0f}s"):
            return False
    return True


def assemble():
    """Merge the two PyInstaller outputs the way the release workflow does."""
    print("\n[3/5] Assemble dist/tickets_hunter")
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    for name in SPECS:
        src = DIST / name / f"{name}{EXE_SUFFIX}"
        if not src.exists():
            return step(f"{name} executable produced", False, str(src))
        shutil.copy2(src, STAGE / src.name)
        if not IS_WINDOWS:
            os.chmod(STAGE / src.name, 0o755)

        internal = DIST / name / "_internal"
        if internal.exists():
            shutil.copytree(internal, STAGE / "_internal", dirs_exist_ok=True)
    step("executables and _internal merged", True)

    # assets/ and www/ are copied from src/ rather than bundled, matching the
    # release workflow -- the settings web UI reads them from disk at runtime.
    for folder in ("assets", "www"):
        shutil.copytree(ROOT / "src" / folder, STAGE / folder,
                        dirs_exist_ok=True)
    step("assets and www copied", True)

    if IS_MACOS:
        launchers = BUILD_SCRIPTS / "macos"
        if launchers.exists():
            # build.command lives beside them but is a developer entry point,
            # not something to ship inside the release bundle.
            shipped = [item for item in launchers.glob("*.command")
                       if item.name != "build.command"]
            for item in shipped:
                shutil.copy2(item, STAGE / item.name)
                os.chmod(STAGE / item.name, 0o755)
            step("macOS launchers copied", True,
                 ", ".join(i.name for i in shipped))
        else:
            step("macOS launchers copied", True,
                 "skipped: build_scripts/macos/ not in this tree")
    return True


def verify_layout():
    print("\n[4/5] Verify layout")
    ok = True
    for name in SPECS:
        exe = STAGE / f"{name}{EXE_SUFFIX}"
        ok &= step(f"{exe.name} exists", exe.exists())
        if exe.exists() and not IS_WINDOWS:
            ok &= step(f"{exe.name} is executable",
                       os.access(exe, os.X_OK))

    ok &= step("_internal present", (STAGE / "_internal").is_dir())
    ok &= step("www/settings.html present",
               (STAGE / "www" / "settings.html").is_file())

    # ddddocr ships its ONNX model as a data file. PyInstaller collects it via
    # collect_data_files(), and a silent miss turns into "OCR always fails" at
    # run time rather than a build error, so it is checked explicitly.
    onnx = list((STAGE / "_internal").rglob("*.onnx"))
    ok &= step("ddddocr model bundled", bool(onnx),
               f"{len(onnx)} .onnx file(s)" if onnx else
               "no .onnx under _internal")

    # The excludes in the spec files were added to keep torch and friends out
    # of the bundle and have never been checked against a real build.
    for unwanted in ("torch", "matplotlib", "IPython"):
        hits = list((STAGE / "_internal").glob(unwanted))
        ok &= step(f"{unwanted} excluded", not hits)

    size_mb = sum(f.stat().st_size for f in STAGE.rglob("*") if f.is_file())
    size_mb /= 1024 * 1024
    step("bundle size", True, f"{size_mb:.0f} MB")
    return ok


def smoke():
    print("\n[5/5] Smoke test")
    exe = STAGE / f"nodriver_tixcraft{EXE_SUFFIX}"
    if not exe.exists():
        return step("bot binary starts", False, "not built")

    try:
        proc = subprocess.run([str(exe), "--help"], cwd=STAGE,
                              capture_output=True, text=True,
                              timeout=SMOKE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return step("bot binary starts", False,
                    f"no output within {SMOKE_TIMEOUT}s")

    output = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        tail = "\n".join(output.strip().splitlines()[-12:])
        print(tail)
        return step("bot binary starts", False,
                    f"exit {proc.returncode}")
    return step("bot binary starts", "--homepage" in output,
                "import chain loaded, argparse reached")


def clear_quarantine():
    """Drop the quarantine flag macOS puts on a freshly written unsigned binary.

    Without it the first launch is refused, and the way out -- right-click,
    Open, confirm -- is not something a user guesses. Whoever just built the
    bundle already trusts it, so the prompt adds friction without adding a
    decision. Handing it to someone else is a different question, and one that
    signing and notarisation answer rather than this.
    """
    proc = subprocess.run(["xattr", "-dr", "com.apple.quarantine", str(STAGE)],
                          capture_output=True, text=True)
    if proc.returncode == 0:
        print("Gatekeeper quarantine flag cleared.")
    else:
        print("Could not clear the quarantine flag, so the first launch will "
              "be blocked. Right-click a .command file and choose Open, or run:")
        print(f"  xattr -dr com.apple.quarantine {STAGE}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-build", action="store_true",
                        help="verify an existing dist/ without rebuilding")
    parser.add_argument("--keep", action="store_true",
                        help="keep build/ for inspecting warn-*.txt")
    args = parser.parse_args()

    print(f"Tickets Hunter local build -- {sys.platform}")
    print(f"Project root: {ROOT}")

    if not preflight():
        print("\nPreflight failed, nothing was built.")
        return 1

    if not args.skip_build:
        if not build():
            print("\nPyInstaller failed. See build/*/warn-*.txt for the "
                  "module it could not resolve.")
            return 1
        if not assemble():
            return 1
    elif not STAGE.exists():
        print(f"\n--skip-build needs an existing {STAGE}")
        return 1

    layout_ok = verify_layout()
    smoke_ok = smoke()

    if not args.keep and (ROOT / "build").exists():
        shutil.rmtree(ROOT / "build")

    failed = [name for name, ok, _ in results if not ok]
    print("\n" + "=" * 60)
    if failed:
        print(f"FAILED ({len(failed)}): " + ", ".join(failed))
        return 1
    print(f"All {len(results)} checks passed")
    print(f"Bundle: {STAGE}")
    if IS_MACOS:
        clear_quarantine()
    return 0 if layout_ok and smoke_ok else 1


if __name__ == "__main__":
    sys.exit(main())
