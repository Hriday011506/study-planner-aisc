# StudyPilot — Heuristic-Based Intelligent Study Planner

StudyPilot is a cloud-deployable study-planning application for an Artificial Intelligence and Cloud Computing course project. It ranks study tasks using **Greedy Best-First Search** and a transparent heuristic.

## Features

- Dashboard for pending tasks, estimated study hours, completion, and next exam
- Priority score based on urgency, difficulty, importance, and workload
- Automatically generated daily study sessions
- Add, edit, and mark tasks completed
- Demo data ready for a presentation
- Workload chart and downloadable CSV timetable
- AI explanation tab for viva demonstrations

## Run locally

Python 3.10+ is recommended.

```bash
git clone https://github.com/Hriday011506/study-planner-aisc.git
cd study-planner-aisc
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Deploy online

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
2. Select **Create app**.
3. Choose repository `Hriday011506/study-planner-aisc`, branch `main`, main file `app.py`.
4. Click **Deploy**. Dependencies install from `requirements.txt`.

No API keys or secrets are required.

## Algorithm

Each pending task receives a heuristic score:

```
h(n) = 10 / (days_until_deadline + 1)
       + 1.4 * difficulty
       + 1.8 * importance
       + 0.25 * min(estimated_hours, 3)
```

Difficulty weights: Easy 1, Moderate 2, Hard 3, Very hard 4.  
Importance weights: Low 1, Normal 2, High 3, Critical 4.

A priority queue selects the highest-score task first. The ranked tasks are then packed into sessions within the selected daily study-hour budget.

- **State:** a pending study task
- **Heuristic:** the task's estimated priority score
- **Frontier:** a priority queue of tasks waiting to be selected
- **Expansion:** remove the highest-scoring task and add it to the ranking
- **Goal:** rank and schedule all pending tasks where available capacity permits

This is **Greedy Best-First Search**. It is simple and explainable but does not guarantee a globally optimal timetable.

## Cloud computing component

Streamlit Community Cloud hosts the web interface and runs the Python algorithm when users interact with it. This demo stores tasks in session state; tasks are not persistently stored across sessions. A database could be added as a future enhancement.

## Project summary

- **Title:** Cloud-Deployed Intelligent Study Planner Using Heuristic Best-First Search
- **Subject:** Artificial Intelligence and Cloud Computing
- **Algorithm:** Greedy Best-First Search with a custom heuristic
- **Technology:** Python, Streamlit, Pandas, Streamlit Community Cloud
