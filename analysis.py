"""CampusPulse - analysis.py
All calculations live here: CSV loading (Pandas), numerical stats (NumPy),
grades, ranking, feedback and academic insights. No web code in this file.
"""
import numpy as np
import pandas as pd

DATA_FILE = "data/students.csv"
SUBJECTS = ["DAA", "DBMS", "OS", "Python", "Maths"]
PASS_MARK = 40          # minimum marks to pass a subject
LOW_ATTENDANCE = 75     # below this = attendance warning
MAX_MARKS = 100


def get_grade(percentage):
    """Convert a percentage to a letter grade."""
    if percentage >= 85: return "A+"
    if percentage >= 75: return "A"
    if percentage >= 60: return "B"
    if percentage >= 50: return "C"
    if percentage >= 40: return "D"
    return "F"


def load_data(path=DATA_FILE):
    """Load the CSV, validate columns, and add calculated columns."""
    df = pd.read_csv(path)
    needed = ["student_id", "name", "section", "attendance"] + SUBJECTS
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"students.csv is missing columns: {missing}")
    df[SUBJECTS + ["attendance"]] = df[SUBJECTS + ["attendance"]].apply(
        pd.to_numeric, errors="coerce").fillna(0).clip(0, 100)

    df["total"] = df[SUBJECTS].sum(axis=1)
    df["percentage"] = (df["total"] / (len(SUBJECTS) * MAX_MARKS) * 100).round(2)
    df["grade"] = df["percentage"].apply(get_grade)
    df["rank"] = df["percentage"].rank(method="min", ascending=False).astype(int)
    # a student passes only if every subject is >= pass mark
    df["result"] = np.where((df[SUBJECTS] >= PASS_MARK).all(axis=1), "Pass", "Fail")
    return df.sort_values("rank").reset_index(drop=True)


def class_summary(df):
    """Overall dashboard numbers."""
    pct = df["percentage"].to_numpy()
    top = df.iloc[0]
    passed = int((df["result"] == "Pass").sum())
    return {
        "total_students": len(df),
        "class_average": round(float(np.mean(pct)), 2),
        "median": round(float(np.median(pct)), 2),
        "std_dev": round(float(np.std(pct)), 2),
        "highest": round(float(pct.max()), 2),
        "lowest": round(float(pct.min()), 2),
        "passed": passed,
        "failed": len(df) - passed,
        "pass_percentage": round(passed / len(df) * 100, 1),
        "avg_attendance": round(float(df["attendance"].mean()), 1),
        "top_name": top["name"], "top_pct": top["percentage"],
        "correlation": round(float(np.corrcoef(df["attendance"], df["percentage"])[0, 1]), 2),
    }


def grade_distribution(df):
    """Number of students per grade (Pandas value_counts)."""
    order = ["A+", "A", "B", "C", "D", "F"]
    return df["grade"].value_counts().reindex(order, fill_value=0)


def section_summary(df):
    """Group by section and aggregate."""
    return df.groupby("section").agg(
        students=("student_id", "count"),
        avg_percentage=("percentage", "mean"),
        avg_attendance=("attendance", "mean"),
        best=("percentage", "max")).round(1).reset_index()


def subject_stats(df):
    """Per-subject statistics using NumPy."""
    rows = []
    for s in SUBJECTS:
        m = df[s].to_numpy()
        rows.append({
            "subject": s, "average": round(float(np.mean(m)), 1),
            "highest": int(m.max()), "lowest": int(m.min()),
            "std_dev": round(float(np.std(m)), 1),
            "passed": int((m >= PASS_MARK).sum()), "failed": int((m < PASS_MARK).sum()),
            "pass_pct": round(float((m >= PASS_MARK).mean() * 100), 1),
            "topper": df.loc[df[s].idxmax(), "name"],
        })
    return pd.DataFrame(rows)


def search_students(df, query="", grade="", result=""):
    """Filter the table by name/ID text, grade and result."""
    out = df
    if query:
        q = query.strip().lower()
        out = out[out["name"].str.lower().str.contains(q) | out["student_id"].str.lower().str.contains(q)]
    if grade:
        out = out[out["grade"] == grade]
    if result:
        out = out[out["result"] == result]
    return out


def student_report(df, student_id):
    """Everything about one student. Returns None if not found."""
    match = df[df["student_id"] == student_id]
    if match.empty:
        return None
    s = match.iloc[0]
    marks = s[SUBJECTS].astype(int)
    avg = df[SUBJECTS].mean()
    return {
        "row": s, "marks": marks, "class_avg": avg.round(1),
        "average": round(float(marks.mean()), 1),
        "best": marks.idxmax(), "worst": marks.idxmin(),
        "failed": [x for x in SUBJECTS if marks[x] < PASS_MARK],
        "feedback": student_feedback(s, marks, avg, df),
    }


def student_feedback(s, marks, avg, df):
    """Rule-based feedback list of (type, text)."""
    fb = []
    p = s["percentage"]
    if p >= 75: fb.append(("good", f"Excellent overall performance ({p}%). Keep it up."))
    elif p >= 60: fb.append(("ok", f"Good performance ({p}%). Small improvements can reach distinction."))
    elif p >= 40: fb.append(("warn", f"Average performance ({p}%). Needs consistent study."))
    else: fb.append(("bad", f"Low performance ({p}%). A structured improvement plan is needed."))
    for sub in SUBJECTS:
        if marks[sub] < PASS_MARK:
            fb.append(("bad", f"Failed in {sub} ({marks[sub]}). Priority subject for revision."))
    fb.append(("ok", f"Strongest: {marks.idxmax()} ({marks.max()}). Weakest: {marks.idxmin()} ({marks.min()})."))
    below = [x for x in SUBJECTS if marks[x] < avg[x] - 10]
    if below:
        fb.append(("warn", "Well below class average in: " + ", ".join(below) + "."))
    if s["attendance"] < LOW_ATTENDANCE:
        fb.append(("warn", f"Attendance is {s['attendance']}%, below the {LOW_ATTENDANCE}% requirement."))
    else:
        fb.append(("good", f"Attendance is healthy at {s['attendance']}%."))
    return fb


def academic_insights(df):
    """Class-level insights as a dict of lists."""
    subs = subject_stats(df)
    weak = subs.sort_values("average").iloc[0]
    low_att = df[df["attendance"] < LOW_ATTENDANCE]
    low_att_avg = low_att["percentage"].mean() if len(low_att) else float("nan")
    high_att_avg = df[df["attendance"] >= LOW_ATTENDANCE]["percentage"].mean()
    corr = class_summary(df)["correlation"]
    return {
        "strong": df[df["percentage"] >= 75],
        "needs_help": df[(df["percentage"] < 50) | (df["result"] == "Fail")],
        "weak_subjects": subs[subs["pass_pct"] < 85].sort_values("pass_pct"),
        "low_attendance": low_att,
        "notes": [
            f"Weakest subject: {weak['subject']} (class average {weak['average']}).",
            f"Strongest subject: {subs.sort_values('average').iloc[-1]['subject']}.",
            f"{len(low_att)} student(s) have attendance below {LOW_ATTENDANCE}%.",
            (f"Students below {LOW_ATTENDANCE}% attendance average {low_att_avg:.1f}% vs "
             f"{high_att_avg:.1f}% for the rest." if len(low_att) else "No attendance problems found."),
            f"Attendance vs percentage correlation is {corr} " +
            ("(strong positive link: attending class improves marks)." if corr >= 0.5 else
             "(weak/moderate link)."),
        ],
    }
