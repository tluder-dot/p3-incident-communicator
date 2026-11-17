"""Rollback drill (06_07_experiments_operations.md §4, governance.md): moves the switch ⏻ through its positions on the prototype,
checks what a customer would get in each one, times it, restores the previous position and logs the test in evals/rollback_tests.csv.
Run it yourself — the log records who pressed it and when:   python prototype/rollback_drill.py "Your Name" "Your role" """
import csv, datetime, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import pipeline, switch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "evals", "rollback_tests.csv")
TICKET = dict(input_type="ticket", received_at_utc="10:02", input="Our EU dashboards stopped updating, is the ingestion down?",
              account_region="EU", plan="self-serve", language="en")


def git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    except OSError:
        return ""


def main():
    who = sys.argv[1] if len(sys.argv) > 1 else git("config", "user.name") or "unknown"
    role = sys.argv[2] if len(sys.argv) > 2 else "switch owner"
    before, checks, t0 = switch.get(), [], time.perf_counter()
    switch.set_position("SUGGEST_ONLY", who, "rollback drill")
    o = pipeline.run_one(TICKET, {})
    checks.append(("SUGGEST_ONLY: draft shown, nothing sendable", o["decision"] == "auto_reply" and not o["sendable"]))
    switch.set_position("OFF", who, "rollback drill")
    o = pipeline.run_one(TICKET, {})
    checks.append(("OFF: humans only, auto-acknowledge rule answers, no incident facts", o["decision"] == "rule_ack" and o["facts_version"] is None))
    switch.set_position("ON", who, "rollback drill")
    o = pipeline.run_one(TICKET, {})
    checks.append(("ON again: approved-facts reply is sendable", o["decision"] == "auto_reply" and o["sendable"]))
    switch.set_position(before, who, "rollback drill: restore")
    seconds = round(time.perf_counter() - t0, 2)
    ok = all(passed for _, passed in checks)
    for name, passed in checks:
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    print(f"\n{'All three positions work' if ok else 'The drill FAILED'} — {seconds} s of machine time, switch restored to {before}.")
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["tested_at_utc", "who", "role", "where", "prototype_commit", "positions_tested", "result", "seconds"])
        w.writerow([datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes"), who, role,
                    "laptop (= staging for the project)", git("rev-parse", "--short", "HEAD"), "SUGGEST_ONLY · OFF · ON",
                    "pass" if ok else "fail", seconds])
    print(f"Logged in {os.path.relpath(LOG, ROOT)} — write the date in governance.md and 06_07 §4 (last tested).")


if __name__ == "__main__":
    main()
