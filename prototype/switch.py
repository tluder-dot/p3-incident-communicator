"""The override switch ⏻ (04_architecture.md §6, governance.md Session 4). Three positions:
ON (as designed: L2 first message, L4 follow-ups) · SUGGEST_ONLY (drafts shown, nothing sendable: L1) · OFF (humans only; the auto-acknowledge rule answers).
Stored in switch.json next to this file, so the IC console, the pipeline and the rollback drill read the same state."""
import datetime, json, os

PATH = os.path.join(os.path.dirname(__file__), "switch.json")
POSITIONS = ("ON", "SUGGEST_ONLY", "OFF")


def get():
    try:
        with open(PATH, encoding="utf-8") as f:
            return json.load(f)["position"]
    except (OSError, ValueError, KeyError):
        return "ON"


def set_position(position, who="unknown", reason=""):
    if position not in POSITIONS:
        raise ValueError(f"position must be one of {POSITIONS}")
    state = {"position": position, "set_by": who, "reason": reason,
             "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return state
