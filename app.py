"""CampusPulse - app.py
Tiny local web server (Python standard library only).
Run:  python app.py   -> opens http://localhost:8000
"""
import html
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# always run from the project folder, whatever folder the terminal is in
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import analysis as an
import charts

PORT = 8000
TEMPLATE = open("templates/page.html", encoding="utf-8").read()
CSS = open("static/style.css", encoding="utf-8").read()

NAV = [("/", "Dashboard"), ("/students", "Students"), ("/subjects", "Subjects"), ("/insights", "Insights")]


# ---------- small HTML helpers ----------
def esc(x):
    return html.escape(str(x))


def card(label, value, sub=""):
    return f'<div class="card"><div class="label">{esc(label)}</div><div class="value">{esc(value)}</div><div class="sub">{esc(sub)}</div></div>'


def table(headers, rows):
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table><tr>{head}</tr>{body}</table>'


def badge(text):
    cls = {"Pass": "good", "Fail": "bad", "A+": "good", "A": "good", "F": "bad"}.get(text, "ok")
    return f'<span class="badge {cls}">{esc(text)}</span>'


def link(row):
    return f'<a href="/student/{esc(row.student_id)}">{esc(row.name)}</a>'


def chart(name, title=""):
    return f'<div class="panel"><img src="/chart/{name}.png" alt="{esc(title)}"></div>'


def student_rows(df):
    return [[r.rank, esc(r.student_id), link(r), f"{r.percentage}%", badge(r.grade), f"{r.attendance:.0f}%", badge(r.result)]
            for r in df.itertuples()]


STUDENT_HEADERS = ["Rank", "ID", "Name", "Percentage", "Grade", "Attendance", "Result"]


# ---------- pages ----------
def dashboard(df, q):
    s = an.class_summary(df)
    cards = "".join([
        card("Total Students", s["total_students"]),
        card("Class Average", f"{s['class_average']}%", f"Std dev {s['std_dev']}"),
        card("Highest", f"{s['highest']}%"),
        card("Lowest", f"{s['lowest']}%"),
        card("Pass Percentage", f"{s['pass_percentage']}%"),
        card("Passed / Failed", f"{s['passed']} / {s['failed']}"),
        card("Top Performer", s["top_name"], f"{s['top_pct']}%"),
        card("Avg Attendance", f"{s['avg_attendance']}%"),
    ])
    sec = an.section_summary(df)
    sec_table = table(["Section", "Students", "Avg %", "Avg Attendance", "Best %"],
                      [[r.section, r.students, r.avg_percentage, r.avg_attendance, r.best] for r in sec.itertuples()])
    body = (f'<div class="cards">{cards}</div><div class="grid">'
            + chart("ranking") + chart("distribution") + chart("grades") + chart("attendance") + "</div>"
            + "<h2>Section-wise Summary (Pandas groupby)</h2>" + sec_table)
    return "Class Dashboard", body


def students(df, q):
    query, grade, result = q.get("q", [""])[0], q.get("grade", [""])[0], q.get("result", [""])[0]
    found = an.search_students(df, query, grade, result)
    opts = lambda items, cur: "".join(f'<option value="{i}"{" selected" if i == cur else ""}>{i or "All"}</option>' for i in items)
    form = (f'<form class="filters"><input name="q" placeholder="Search name or ID" value="{esc(query)}">'
            f'<select name="grade">{opts(["", "A+", "A", "B", "C", "D", "F"], grade)}</select>'
            f'<select name="result">{opts(["", "Pass", "Fail"], result)}</select><button>Filter</button></form>')
    return "Students & Ranking", form + f"<p>{len(found)} student(s) found. Click a name for the full analysis.</p>" + table(STUDENT_HEADERS, student_rows(found))


def student_page(df, sid):
    r = an.student_report(df, sid)
    if r is None:
        return None
    s = r["row"]
    cards = "".join([
        card("Total Marks", f"{int(s['total'])} / {len(an.SUBJECTS) * 100}"),
        card("Average", r["average"]), card("Percentage", f"{s['percentage']}%"),
        card("Grade", s["grade"]), card("Class Rank", f"{s['rank']} of {len(df)}"),
        card("Attendance", f"{s['attendance']:.0f}%"), card("Strongest", r["best"]), card("Weakest", r["worst"]),
    ])
    marks = table(["Subject", "Marks", "Class Avg", "Difference", "Status"],
                  [[sub, r["marks"][sub], r["class_avg"][sub], f"{r['marks'][sub] - r['class_avg'][sub]:+.1f}",
                    badge("Pass" if r["marks"][sub] >= an.PASS_MARK else "Fail")] for sub in an.SUBJECTS])
    fb = "".join(f'<li class="{t}">{esc(x)}</li>' for t, x in r["feedback"])
    body = (f'<p>{esc(s["student_id"])} &bull; Section {esc(s["section"])} &bull; Result: {badge(s["result"])}</p>'
            f'<div class="cards">{cards}</div><div class="grid">'
            f'{chart("student/" + sid + "/marks")}{chart("student/" + sid + "/position")}</div>'
            f'<h2>Subject Marks</h2>{marks}<h2>Performance Feedback</h2><ul class="feedback">{fb}</ul>')
    return s["name"], body


def subjects(df, q):
    st = an.subject_stats(df)
    t = table(["Subject", "Average", "Highest", "Lowest", "Std Dev", "Passed", "Failed", "Pass %", "Topper"],
              [[r.subject, r.average, r.highest, r.lowest, r.std_dev, r.passed, r.failed, r.pass_pct, esc(r.topper)] for r in st.itertuples()])
    return "Subject Analysis", t + '<div class="grid">' + chart("subject_averages") + chart("subject_pass_fail") + "</div>"


def insights(df, q):
    i = an.academic_insights(df)
    names = lambda d: ", ".join(link(r) for r in d.itertuples()) or "None"
    notes = "".join(f"<li>{esc(n)}</li>" for n in i["notes"])
    weak = table(["Subject", "Pass %", "Average"], [[r.subject, r.pass_pct, r.average] for r in i["weak_subjects"].itertuples()]) if len(i["weak_subjects"]) else "<p>All subjects have a healthy pass rate.</p>"
    body = (f'<h2>Class Observations</h2><ul class="feedback">{notes}</ul>'
            f'<h2>Strong Students (75%+)</h2><p>{names(i["strong"])}</p>'
            f'<h2>Students Needing Improvement</h2><p>{names(i["needs_help"])}</p>'
            f'<h2>Low Attendance</h2><p>{names(i["low_attendance"])}</p>'
            f'<h2>Weak Subjects (pass rate below 85%)</h2>{weak}')
    return "Academic Insights", body


ROUTES = {"/": dashboard, "/students": students, "/subjects": subjects, "/insights": insights}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, data, ctype, code=200):
        data = data.encode("utf-8") if isinstance(data, str) else data
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def page(self, path, result, code=200):
        title, body = result
        nav = "".join(f'<a href="{u}" class="{"active" if u == path or (u == "/students" and path.startswith("/student/")) else ""}">{n}</a>' for u, n in NAV)
        self.send(TEMPLATE.replace("{{title}}", esc(title)).replace("{{nav}}", nav).replace("{{body}}", body), "text/html; charset=utf-8", code)

    def do_GET(self):
        url = urlparse(self.path)
        path, q = url.path, parse_qs(url.query)
        df = an.load_data()          # reload CSV on every request: edit the file, refresh the page
        if path == "/style.css":
            return self.send(CSS, "text/css")
        if path.startswith("/chart/"):
            return self.chart(df, path[7:-4])
        if path in ROUTES:
            return self.page(path, ROUTES[path](df, q))
        if path.startswith("/student/"):
            result = student_page(df, path.split("/")[-1])
            if result:
                return self.page(path, result)
        self.page(path, ("Not found", "<p>Page not found. <a href='/'>Go to dashboard</a></p>"), 404)

    def chart(self, df, name):
        parts = name.split("/")
        if name in charts.CLASS_CHARTS:
            png = charts.CLASS_CHARTS[name](df)
        elif len(parts) == 3 and parts[0] == "student" and parts[1:] and parts[1] in set(df["student_id"]):
            png = (charts.student_marks if parts[2] == "marks" else charts.student_rank_position)(df, parts[1])
        else:
            return self.send("Not found", "text/plain", 404)
        self.send(png, "image/png")


def main():
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"CampusPulse running at {url}  (press Ctrl+C to stop)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
