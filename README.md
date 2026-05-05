# StudyIQ — Smart Learning Analytics & Recommendation System

> A full-stack academic analytics platform built with Flask,
> helping CS students track their learning journey and prepare
> smarter for campus placements.

---

## Problem Statement

CS students preparing for placements study from multiple platforms
but have no unified system to track progress, identify weak areas,
or measure real growth. This platform solves that by acting as a
personal academic analytics engine.

---

## Features

- Daily study session logging (subject, topic, accuracy, time)
- 5-metric scoring engine — accuracy, frequency, recency, consistency, productivity
- Placement readiness score with subject-weighted formula
- 7-rule intelligent recommendation engine
- Subject and topic-wise performance dashboard
- Weekly and monthly progress reports
- Streak tracking and consistency scoring
- Paginated session history with delete support

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3.0 |
| Database | SQLite + Flask-SQLAlchemy |
| Auth | Flask-Login + Werkzeug |
| Frontend | Bootstrap 5, Jinja2, Chart.js |
| Testing | Postman |
| Deployment | Render |

---

## Project Structure

```text
smart_learning_analytics/
├── app.py                 # Flask app factory and all routes
├── models.py              # SQLAlchemy database models
├── analytics.py           # Scoring and analytics engine
├── recommendation.py      # Recommendation engine
├── config.py              # Environment-based configuration
├── requirements.txt       # Python dependencies
├── Procfile               # Deployment configuration
├── templates/             # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── log_study.html
│   ├── weekly_report.html
│   ├── monthly_report.html
│   └── history.html
└── static/
├── css/style.css
└── js/charts.js
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-learning-analytics.git
cd smart-learning-analytics
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

### 5. Open in browser
http://127.0.0.1:5000


Database and subjects are seeded automatically on first run.

---

## API Endpoints

| Route | Method | Description |
|---|---|---|
| `/` | GET | Landing page |
| `/register` | POST | User registration |
| `/login` | POST | User login |
| `/dashboard` | GET | Analytics dashboard |
| `/log-study` | POST | Log study session |
| `/analytics` | GET | JSON analytics data |
| `/recommendations` | GET | JSON recommendations |
| `/weekly-report` | GET | Weekly summary |
| `/monthly-report` | GET | Monthly summary |
| `/history` | GET | Paginated session history |
| `/api/topics/<id>` | GET | Topics for a subject |

---

## Scoring Formula

Topic Health     = (Accuracy × 0.50) + (Frequency × 0.30) + (Recency × 0.20)
Subject Score    = Average of topic health scores
Placement Score  = Weighted average (DSA 30%, DBMS 20%, OS 15%, CN 15%, Aptitude 20%)
Overall Score    = (Placement × 0.70) + (Consistency × 0.25) + Streak Bonus

---

## Future Scope

- ML-based score prediction using historical session data
- PostgreSQL migration for production persistence
- LeetCode API integration for automatic solve tracking
- Mobile responsive PWA version
- Peer comparison and leaderboard

---

