"""Grading sheets for the two human graders and the agreement rates (evals/judge_rubric.md · Assignment 5 §5).
  python prototype/grading.py sheet evals/eval_set_v1.csv evals/outputs_v1.csv OUT_DIR P3-01,P3-02,...  -> two identical blind sheets
  python prototype/grading.py agree evals/grades/grader_A.csv evals/grades/grader_B.csv [evals/grades/judge.csv]
Graders never see the labels of the eval-set or each other's sheet."""
import os, sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASE_COLS = ["case_id", "input_type", "received_at_utc", "account_region", "plan", "language", "context", "input"]
GRADE_COLS = ["c1_right_to_answer", "c2_right_incident", "c3_facts_in_force", "c4_nothing_unapproved", "c5_sendable", "verdict", "reason"]


def sheet(eval_csv, outputs_csv, out_dir, ids):
    cases = pd.read_csv(eval_csv, dtype=str).fillna("").set_index("case_id")
    outs = pd.read_csv(outputs_csv, dtype=str).fillna("").set_index("case_id")
    rubric = open(os.path.join(ROOT, "evals", "judge_rubric.md"), encoding="utf-8").read().splitlines()
    for grader in ("A", "B"):
        wb = Workbook()
        ws = wb.active
        ws.title = "Guideline"
        ws.append([f"Grader {grader} — your name:", ""])
        ws.append(["Grade alone. Fill the yellow columns of the sheet 'Grade these'. Do not look at the other grader's sheet."])
        for line in rubric:
            ws.append([line])
        ws.column_dimensions["A"].width = 160
        g = wb.create_sheet("Grade these")
        header = CASE_COLS + ["agent_decision", "agent_reason", "agent_text"] + GRADE_COLS
        g.append(header)
        for cid in ids:
            c, o = cases.loc[cid], outs.loc[cid]
            g.append([cid] + [c[k] for k in CASE_COLS[1:]] + [o["decision"], o["reason"], o["output"]] + [""] * len(GRADE_COLS))
        widths = dict(case_id=8, input_type=12, received_at_utc=9, account_region=9, plan=10, language=8, context=40, input=55,
                      agent_decision=14, agent_reason=30, agent_text=70, verdict=12, reason=40)
        for j, name in enumerate(header, 1):
            col = g.cell(1, j).column_letter
            g.column_dimensions[col].width = widths.get(name, 11)
            g.cell(1, j).font = Font(bold=True)
            for i in range(1, len(ids) + 2):
                g.cell(i, j).alignment = Alignment(wrap_text=True, vertical="top")
                if name in GRADE_COLS and i > 1:
                    g.cell(i, j).fill = PatternFill("solid", fgColor="FFF4CC")
        yn = DataValidation(type="list", formula1='"YES,NO"', allow_blank=True)
        vd = DataValidation(type="list", formula1='"SEND,EDIT,ESCALATE"', allow_blank=True)
        g.add_data_validation(yn)
        g.add_data_validation(vd)
        first, last = len(CASE_COLS) + 4, len(CASE_COLS) + 8
        yn.add(f"{g.cell(2, first).column_letter}2:{g.cell(2, last).column_letter}{len(ids) + 1}")
        vd.add(f"{g.cell(2, last + 1).column_letter}2:{g.cell(2, last + 1).column_letter}{len(ids) + 1}")
        g.freeze_panes = g.cell(2, len(CASE_COLS) + 4)
        path = os.path.join(out_dir, f"GRADER_{grader}_grade_{len(ids)}_cases.xlsx")
        wb.save(path)
        print("saved", path)


def read(path):
    if path.endswith(".xlsx"):
        df = pd.read_excel(path, sheet_name="Grade these", dtype=str)
    else:
        df = pd.read_csv(path, dtype=str)
    df = df.fillna("")
    df["verdict"] = df["verdict"].str.strip().str.upper()
    return df.set_index("case_id")


def agree(a_path, b_path, judge_path=None):
    a, b = read(a_path), read(b_path)
    ids = [i for i in a.index if a.loc[i, "verdict"] and b.loc[i, "verdict"]]
    same = [i for i in ids if a.loc[i, "verdict"] == b.loc[i, "verdict"]]
    print(f"human–human agreement: {len(same)}/{len(ids)} = {len(same) / len(ids):.0%}")
    for i in ids:
        if i not in same:
            print(f"  {i}: A {a.loc[i, 'verdict']} ({a.loc[i, 'reason']}) · B {b.loc[i, 'verdict']} ({b.loc[i, 'reason']})")
    result = {"n": len(ids), "human_human": len(same) / len(ids)}
    if judge_path:
        j = read(judge_path)
        both = [i for i in same if i in j.index]
        hit = [i for i in both if j.loc[i, "verdict"] == a.loc[i, "verdict"]]
        print(f"human–judge agreement (on the {len(both)} cases where both humans agree): {len(hit)}/{len(both)} = {len(hit) / len(both):.0%}")
        for name, h in (("A", a), ("B", b)):
            k = [i for i in ids if i in j.index and j.loc[i, "verdict"] == h.loc[i, "verdict"]]
            print(f"  judge vs grader {name}: {len(k)}/{len(ids)} = {len(k) / len(ids):.0%}")
        for i in both:
            if i not in hit:
                print(f"  {i}: humans {a.loc[i, 'verdict']} · judge {j.loc[i, 'verdict']} ({j.loc[i, 'reason'][:90]})")
        result["human_judge"] = len(hit) / len(both)
    return result


if __name__ == "__main__":
    if sys.argv[1] == "sheet":
        sheet(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].split(","))
    else:
        agree(*sys.argv[2:5])
