"""CampusPulse - charts.py
Every chart is drawn with Matplotlib and returned as PNG bytes.
"""
import io
import matplotlib
matplotlib.use("Agg")           # draw without opening a window
import matplotlib.pyplot as plt
import numpy as np
from analysis import SUBJECTS, PASS_MARK, LOW_ATTENDANCE, subject_stats, grade_distribution

BLUE, GREY, RED, GREEN = "#2f5bea", "#b8c0d4", "#e5484d", "#2da44e"


def to_png(fig):
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=110)
    plt.close(fig)
    return buf.getvalue()


def _clean(ax):
    ax.spines[["top", "right"]].set_visible(False)


def subject_averages(df):
    st = subject_stats(df)
    fig, ax = plt.subplots(figsize=(6, 3.8))
    bars = ax.bar(st["subject"], st["average"], color=BLUE)
    ax.bar_label(bars, fmt="%.1f")
    ax.axhline(PASS_MARK, color=RED, ls="--", label="Pass mark")
    ax.set(ylim=(0, 100), ylabel="Average marks", title="Subject-wise Class Average")
    ax.legend(); _clean(ax)
    return to_png(fig)


def distribution(df):
    fig, ax = plt.subplots(figsize=(6, 3.8))
    counts, edges = np.histogram(df["percentage"], bins=np.arange(30, 101, 10))
    ax.bar(edges[:-1] + 5, counts, width=9, color=BLUE)
    mean = df["percentage"].mean()
    ax.axvline(mean, color=RED, ls="--", label=f"Mean {mean:.1f}%")
    ax.set(xlabel="Percentage", ylabel="Students", title="Percentage Distribution")
    ax.legend(); _clean(ax)
    return to_png(fig)


def grades(df):
    gd = grade_distribution(df)
    fig, ax = plt.subplots(figsize=(6, 3.8))
    bars = ax.bar(gd.index, gd.values, color=[GREEN, GREEN, BLUE, BLUE, GREY, RED])
    ax.bar_label(bars)
    ax.set(ylabel="Students", title="Grade Distribution"); _clean(ax)
    return to_png(fig)


def ranking(df):
    top = df.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.barh(top["name"], top["percentage"], color=BLUE)
    ax.set(xlim=(0, 100), xlabel="Percentage", title="Top 10 Students")
    ax.bar_label(ax.containers[0], fmt="%.1f"); _clean(ax)
    return to_png(fig)


def attendance(df):
    fig, ax = plt.subplots(figsize=(6, 3.8))
    low = df["attendance"] < LOW_ATTENDANCE
    ax.scatter(df.loc[~low, "attendance"], df.loc[~low, "percentage"], color=BLUE, label="OK")
    ax.scatter(df.loc[low, "attendance"], df.loc[low, "percentage"], color=RED, label="Low attendance")
    slope, intercept = np.polyfit(df["attendance"], df["percentage"], 1)   # trend line
    xs = np.array([df["attendance"].min(), df["attendance"].max()])
    ax.plot(xs, slope * xs + intercept, color=GREY, ls="--", label="Trend")
    ax.axvline(LOW_ATTENDANCE, color=RED, ls=":", lw=1)
    ax.set(xlabel="Attendance %", ylabel="Percentage", title="Attendance vs Performance")
    ax.legend(); _clean(ax)
    return to_png(fig)


def subject_pass_fail(df):
    st = subject_stats(df)
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.bar(st["subject"], st["passed"], color=GREEN, label="Passed")
    ax.bar(st["subject"], st["failed"], bottom=st["passed"], color=RED, label="Failed")
    ax.set(ylabel="Students", title="Pass / Fail by Subject")
    ax.legend(); _clean(ax)
    return to_png(fig)


def student_marks(df, student_id):
    s = df[df["student_id"] == student_id].iloc[0]
    x = np.arange(len(SUBJECTS))
    fig, ax = plt.subplots(figsize=(6, 3.8))
    bars = ax.bar(x - 0.2, s[SUBJECTS].astype(int), 0.4, color=BLUE, label=s["name"])
    ax.bar(x + 0.2, df[SUBJECTS].mean(), 0.4, color=GREY, label="Class average")
    ax.bar_label(bars)
    ax.axhline(PASS_MARK, color=RED, ls="--", lw=1)
    ax.set_xticks(x, SUBJECTS)
    ax.set(ylim=(0, 105), ylabel="Marks", title="Student vs Class Average")
    ax.legend(); _clean(ax)
    return to_png(fig)


def student_rank_position(df, student_id):
    """Where the student stands among the whole class (sorted percentages)."""
    ordered = df.sort_values("percentage")
    colors = [RED if i == student_id else GREY for i in ordered["student_id"]]
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.bar(range(len(ordered)), ordered["percentage"], color=colors)
    ax.set(xlabel="Students (lowest to highest)", ylabel="Percentage", title="Position in Class (red = this student)")
    ax.set_xticks([]); _clean(ax)
    return to_png(fig)


CLASS_CHARTS = {"subject_averages": subject_averages, "distribution": distribution,
                "grades": grades, "ranking": ranking, "attendance": attendance,
                "subject_pass_fail": subject_pass_fail}
