# 📊 CampusPulse — Academic Analytics System

**CampusPulse** is a Python-based academic analytics mini-project that analyzes student marks and attendance to generate academic performance insights through an interactive web dashboard.

Built using **Python, Pandas, NumPy, and Matplotlib**, it helps visualize student performance, identify low attendance, analyze subject-wise results, and understand academic trends.

## ✨ Features

- 📈 **Performance Dashboard** — View overall academic statistics and performance summaries.
- 👨‍🎓 **Student Analysis** — Search and filter student records and view rankings.
- 📚 **Subject-Wise Analysis** — Analyze marks across different subjects.
- 📊 **Data Visualization** — Generate charts to understand student performance and trends.
- 💡 **Academic Insights** — Identify students with low attendance and highlight areas that need improvement.
- 🔄 **CSV-Based Data** — Load and update student records using a CSV file.
- 🌐 **Local Web Interface** — Access the dashboard through your browser.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic and web server |
| Pandas | Data loading, filtering, grouping, and analysis |
| NumPy | Numerical calculations and statistical operations |
| Matplotlib | Charts and data visualization |
| HTML & CSS | Dashboard layout and styling |
| CSV | Student academic dataset |

## 📁 Project Structure

```text
CampusPulse/
├── app.py
├── analysis.py
├── charts.py
├── requirements.txt
├── README.md
├── data/
│   └── students.csv
├── templates/
│   └── page.html
└── static/
    └── style.css
```

## 🚀 Getting Started

### Prerequisites

- Python installed on your system
- pip package installer

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/Adimodgil/CampusPulse.git
cd CampusPulse
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the application**

```bash
python app.py
```

**4. Open the dashboard**

Visit [http://localhost:8000](http://localhost:8000) in your browser if it does not open automatically.

## 📋 Academic Rules

- A student passes when they score at least 40 marks in every subject.
- Grades are assigned according to the thresholds implemented in the project.
- Attendance below 75% is considered low attendance.
- Updated records can be analyzed by editing the student CSV dataset and refreshing the application.

## 📊 Data Analysis

CampusPulse uses:

- **Pandas:** CSV loading, grouping, aggregation, ranking, sorting, and filtering.
- **NumPy:** Mean, standard deviation, median, histogram calculations, correlation, and polynomial fitting.
- **Matplotlib:** Bar charts, horizontal bar charts, scatter plots, and histograms.

## 🎯 Project Objective

The objective of CampusPulse is to demonstrate how Python data analysis and visualization libraries can be combined to build a simple academic analytics system that presents student performance data in a useful and understandable format.

## 👨‍💻 Author

**Aditya Modgil**

GitHub: [@Adimodgil](https://github.com/Adimodgil)

---

*CampusPulse — Turning academic data into meaningful insights.*
