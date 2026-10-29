# CampusPulse — MCA • Python Academic Analytics

A mini project that analyses student marks and attendance with **Pandas, NumPy and Matplotlib** and shows the results in a browser on localhost.

## Run

```bash
pip install -r requirements.txt
python app.py
```

The browser opens at http://localhost:8000 (open it manually if it does not).

## Files

| File | Purpose |
|---|---|
| `analysis.py` | Pandas + NumPy: loading CSV, grades, ranks, stats, feedback, insights |
| `charts.py` | Matplotlib charts (returned as PNG) |
| `app.py` | Small `http.server` web server + HTML building |
| `templates/page.html`, `static/style.css` | One reusable page layout and simple CSS |
| `data/students.csv` | 30 students: ID, name, section, attendance, 5 subject marks |

## Pages

Dashboard · Students (search/filter + ranking) · Student analysis (`/student/CP101`) · Subjects · Insights

## Rules used

Pass = at least 40 in every subject. Grades: A+ ≥85, A ≥75, B ≥60, C ≥50, D ≥40, else F.

Low attendance = below 75%. Edit `students.csv` and refresh the page to see new results.

## Viva pointers

- **Pandas:** `read_csv`, `groupby/agg`, `sort_values`, `rank`, `value_counts`, boolean filtering
- **NumPy:** `mean`, `std`, `median`, `histogram`, `corrcoef`, `polyfit`
- **Matplotlib:** bar, barh, scatter, histogram — drawn to memory with the `Agg` backend
