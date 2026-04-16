#!/usr/bin/env python3
"""
local_ci.py — Simulate the CI/CD pipeline locally
===================================================
Run this to mimic exactly what GitHub Actions / Jenkins does,
without needing any external service.

Usage:
    python local_ci.py
"""

import subprocess
import sys
import time
import os
import signal

REPORTS_DIR = "reports"
SERVER_PID  = None


def step(title):
    print(f"\n{'='*60}")
    print(f"  STAGE: {title}")
    print(f"{'='*60}")


def run(cmd, capture=False):
    print(f"$ {cmd}")
    result = subprocess.run(
        cmd, shell=True,
        capture_output=capture, text=True
    )
    if result.returncode != 0:
        print(f"\n❌  Command failed (exit {result.returncode})")
        if capture:
            print(result.stdout)
            print(result.stderr)
        stop_server()
        sys.exit(result.returncode)
    return result


def start_server():
    global SERVER_PID
    step("Start Flask Server")
    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    SERVER_PID = proc.pid
    print(f"Flask server started (PID {SERVER_PID}). Waiting 3 s...")
    time.sleep(3)
    print("✅  Server is up.")


def stop_server():
    global SERVER_PID
    if SERVER_PID:
        print(f"\n🛑  Stopping Flask server (PID {SERVER_PID})...")
        try:
            os.kill(SERVER_PID, signal.SIGTERM)
        except ProcessLookupError:
            pass
        SERVER_PID = None


def main():
    print("\n" + "🔄 " * 20)
    print("  LOCAL CI/CD PIPELINE SIMULATION")
    print("🔄 " * 20)

    os.makedirs(REPORTS_DIR, exist_ok=True)

    # ── Stage 1: Lint ────────────────────────────────────────
    step("Lint  (flake8)")
    run("flake8 app.py test_api.py --max-line-length=120 --count")
    print("✅  Lint passed.")

    # ── Stage 2: Start server ────────────────────────────────
    start_server()

    # ── Stage 3: Run tests ───────────────────────────────────
    step("Run Tests  (pytest)")
    run(
        f"pytest test_api.py -v "
        f"--tb=short "
        f"--junitxml={REPORTS_DIR}/results.xml "
        f"--cov=app "
        f"--cov-report=term-missing "
        f"--cov-report=xml:{REPORTS_DIR}/coverage.xml"
    )
    print("✅  All tests passed.")

    # ── Stage 4: Coverage summary ────────────────────────────
    step("Coverage Summary")
    run("python -m coverage report")

    # ── Stage 5: Stop server ─────────────────────────────────
    stop_server()

    # ── Done ─────────────────────────────────────────────────
    print("\n" + "✅ " * 20)
    print("  PIPELINE COMPLETE — All stages passed!")
    print(f"  Reports saved in: ./{REPORTS_DIR}/")
    print("✅ " * 20 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        stop_server()
        sys.exit(1)
