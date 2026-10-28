import heapq
import itertools
import io
import re
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="StudyPilot", page_icon="assets/studypilot-logo.svg", layout="wide", initial_sidebar_state="expanded")

# Use Streamlit-native components for reliable contrast and responsive rendering.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { color-scheme: light; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:#f6f8fc; color:#18243b; }
.block-container { max-width:1240px; padding:1.7rem 2.2rem 3rem; }
h1,h2,h3,h4 { font-family:'Manrope',sans-serif !important; color:#172642 !important; letter-spacing:-.35px; }
p, label, .stMarkdown, [data-testid="stWidgetLabel"] { color:#34435d; }
[data-testid="stSidebar"] { background:#fff; border-right:1px solid #e4e9f2; }
[data-testid="stSidebar"] * { color:#24344f; }
[data-testid="stMetric"] { background:#fff; border:1px solid #e2e8f2; border-radius:15px; padding:17px 18px; box-shadow:0 4px 14px rgba(24,42,76,.035); }
[data-testid="stMetricLabel"] { color:#64718a !important; font-size:.84rem; }
[data-testid="stMetricValue"] { color:#172b4d !important; font-weight:800; }
[data-testid="stMetricDelta"] { color:#227653 !important; }
[data-baseweb="select"] > div { background:#fff !important; color:#1d2b45 !important; border-color:#d9e0ec !important; border-radius:9px !important; }
[data-baseweb="select"] input, [data-baseweb="select"] span { color:#1d2b45 !important; }
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] { background:#fff !important; color:#1d2b45 !important; }
[role="option"] { color:#1d2b45 !important; }
input, textarea { background:#fff !important; color:#1d2b45 !important; border-color:#d9e0ec !important; }
[data-testid="stNumberInput"] button { background:#f1f4fa !important; color:#1d2b45 !important; border-color:#d9e0ec !important; }
[data-testid="stTabs"] { margin-top:1.4rem; }
[data-testid="stTabs"] button { font-weight:700; color:#52617a !important; padding: .75rem 1rem; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#4055be !important; }
.stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button { border-radius:10px; font-weight:700; min-height:2.65rem; }
.stButton button:not([kind="primary"]), .stDownloadButton button { background:#fff !important; color:#253650 !important; border:1px solid #d9e1ee !important; }
.stButton button:not([kind="primary"]):hover, .stDownloadButton button:hover { background:#f1f4fb !important; border-color:#aab7d3 !important; }
.stButton button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] { background:#485bc4 !important; border:1px solid #485bc4 !important; color:#fff !important; }
.stButton button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button[kind="primary"]:hover { background:#394ba9 !important; color:#fff !important; }
div[data-testid="stForm"] { background:#fff; border:1px solid #e2e8f2; border-radius:15px; padding:20px; }
div[data-testid="stDataFrame"] { background:#fff; border:1px solid #e2e8f2; border-radius:11px; }
hr { border-color:#e2e8f2; }
.section-heading { display:flex; align-items:end; justify-content:space-between; gap:1rem; margin:1.7rem 0 .9rem; }
.section-eyebrow { color:#5264c9; font-size:.72rem; font-weight:800; letter-spacing:1.4px; text-transform:uppercase; margin-bottom:4px; }
.section-caption { color:#73809a; font-size:.88rem; }
.exam-card { background:#fff; border:1px solid #e1e7f2; border-radius:16px; padding:17px 18px; min-height:150px; box-shadow:0 4px 14px rgba(24,42,76,.035); }
.exam-card .exam-subject { color:#7a859b; font-size:.75rem; font-weight:800; text-transform:uppercase; letter-spacing:1px; }
.exam-card .exam-days { font-family:'Manrope',sans-serif; font-size:2rem; line-height:1.1; font-weight:800; color:#1c2d50; margin:10px 0 5px; }
.exam-card .exam-date { color:#586984; font-size:.85rem; }
.exam-card .exam-tag { display:inline-block; margin-top:12px; border-radius:99px; padding:4px 9px; background:#edf1ff; color:#4053bd; font-size:.72rem; font-weight:800; }
.exam-card.urgent { border-color:#ffd8cf; background:#fffaf8; }
.exam-card.urgent .exam-days { color:#bd4d37; }
.exam-card.urgent .exam-tag { background:#fff0eb; color:#b94b35; }
.progress-wrap { background:#fff; border:1px solid #e1e7f2; border-radius:15px; padding:16px 19px; margin:15px 0 5px; }
.progress-title { font-weight:800; color:#1c2d50; }
.progress-sub { color:#748099; font-size:.82rem; margin-top:4px; }
.hero { background:linear-gradient(120deg,#eaf0ff 0%,#f5f7ff 100%); border:1px solid #dce5ff; border-radius:20px; padding:32px 34px; margin-bottom:24px; }
.hero .eyebrow { color:#4055be; font-size:.72rem; font-weight:800; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:10px; }
.hero h1 { font-size:2.15rem; line-height:1.17; margin:0; color:#172642 !important; }
.hero p { color:#465773; font-size:1rem; margin:.8rem 0 0; max-width:780px; line-height:1.65; }
.task-card { background:#fff; border:1px solid #e2e8f2; border-radius:13px; padding:16px 18px; margin-bottom:11px; box-shadow:0 3px 10px rgba(24,42,76,.025); }
.task-time { color:#65728a; font-size:.82rem; font-weight:700; }
.task-title { color:#172b4d; font-size:1.02rem; font-weight:800; margin:6px 0; }
.task-meta { color:#596983; font-size:.88rem; }
div[data-testid="stAlert"] { border-radius:11px; }
@media (max-width:800px) { .block-container { padding:1rem .8rem 2rem; } .hero { padding:22px; } .hero h1 { font-size:1.6rem; } }
</style>
""", unsafe_allow_html=True)

IMPORTANCE = {"Low": 1, "Normal": 2, "High": 3, "Critical": 4}
DIFFICULTY = {"Easy": 1, "Moderate": 2, "Hard": 3, "Very hard": 4}

def extract_topics(uploaded_file):
    """Extract likely syllabus topics from PDF, DOCX, or plain-text handouts."""
    filename = uploaded_file.name.lower()
    raw = uploaded_file.getvalue()
    text = ""
    if filename.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif filename.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(raw))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text.strip() for cell in row.cells if cell.text.strip()))
        text = "\n".join(parts)
    else:
        text = raw.decode("utf-8", errors="ignore")
    lines = [re.sub(r"\s+", " ", line).strip(" •\t-–—") for line in text.splitlines()]
    lines = [line for line in lines if len(line) >= 3]
    topics = []
    seen = set()
    heading_pattern = re.compile(r"^(?:(?:unit|module|chapter|lecture|week|topic|experiment)\s*(?:[0-9ivx]+)?\s*[:.\-–)]?\s*|(?:[0-9]+(?:\.[0-9]+)*[.)]?\s+))(.+)$", re.I)
    generic_labels = {"contents", "table of contents", "course outcomes", "references", "text books", "textbooks", "assessment", "evaluation", "syllabus"}
    for line in lines:
        clean = re.sub(r"\s+", " ", line).strip()
        match = heading_pattern.match(clean)
        candidate = match.group(1).strip(" :.-") if match else clean
        if candidate.lower() in generic_labels:
            continue
        is_bullet = line != clean or re.match(r"^[•*▪◦-]\s+", line) is not None
        is_heading = match is not None or (len(clean) <= 90 and clean.isupper() and len(clean.split()) <= 12)
        looks_like_topic = any(word in candidate.lower() for word in ["search", "algorithm", "learning", "network", "logic", "agent", "model", "cloud", "knowledge", "game", "neural", "fuzzy", "genetic", "planning", "optimization", "optimization", "module", "unit", "introduction", "architecture", "classification", "regression", "analysis", "management", "security", "computing", "programming", "data", "system", "design", "testing", "heuristic", "hill climbing", "best-first", "a*"])
        if (is_bullet or is_heading or looks_like_topic) and 3 <= len(candidate) <= 120:
            key = candidate.lower()
            if key not in seen and not re.match(r"^(page|figure|table)\s+\d+", key):
                seen.add(key)
                topics.append(candidate)
    # Keep the list useful and avoid turning whole paragraphs into topics.
    topics = [t for t in topics if len(t.split()) <= 18]
    return text, topics[:100]
def demo_tasks(today):
    return [
        {"Subject":"Artificial Intelligence","Task":"Heuristic search revision","Exam date":today+timedelta(days=3),"Hours":1.5,"Difficulty":"Moderate","Importance":"High","Status":"Pending","Notes":"Best-First Search, Hill Climbing, A*"},
        {"Subject":"Computer Networks","Task":"Subnetting practice","Exam date":today+timedelta(days=2),"Hours":2.0,"Difficulty":"Hard","Importance":"Critical","Status":"Pending","Notes":"Practice CIDR and VLSM"},
        {"Subject":"Artificial Intelligence","Task":"State-space problem practice","Exam date":today+timedelta(days=3),"Hours":1.0,"Difficulty":"Moderate","Importance":"High","Status":"Pending","Notes":"Trace states and solution paths"},
        {"Subject":"Software Engineering","Task":"UML diagrams","Exam date":today+timedelta(days=5),"Hours":1.5,"Difficulty":"Moderate","Importance":"Normal","Status":"Pending","Notes":"Use-case, activity, sequence"},
        {"Subject":"Computer Networks","Task":"TCP and congestion control","Exam date":today+timedelta(days=2),"Hours":1.0,"Difficulty":"Moderate","Importance":"High","Status":"Pending","Notes":"Slow start and AIMD"},
        {"Subject":"Cloud Computing","Task":"Service and deployment models","Exam date":today+timedelta(days=7),"Hours":1.5,"Difficulty":"Moderate","Importance":"Normal","Status":"Pending","Notes":"IaaS, PaaS, SaaS"},
        {"Subject":"Artificial Intelligence","Task":"Practice questions","Exam date":today+timedelta(days=3),"Hours":1.0,"Difficulty":"Easy","Importance":"Normal","Status":"Pending","Notes":"Try questions before viewing solutions"},
    ]

def heuristic(task, today):
    days = max(0, (task["Exam date"] - today).days)
    urgency = 10 / (days + 1)
    difficulty = DIFFICULTY.get(task["Difficulty"], 2) * 1.4
    importance = IMPORTANCE.get(task["Importance"], 2) * 1.8
    workload = min(float(task["Hours"]), 3) * 0.25
    return round(urgency + difficulty + importance + workload, 2)

def best_first_search(tasks, today):
    """Greedy Best-First Search ranks tasks by the highest heuristic score."""
    frontier, counter = [], itertools.count()
    for task in tasks:
        heapq.heappush(frontier, (-heuristic(task, today), next(counter), task))
    ranked = []
    while frontier:
        negative_score, _, task = heapq.heappop(frontier)
        ranked.append({**task, "Priority score": round(-negative_score, 2),
                       "Days left": max(0, (task["Exam date"] - today).days)})
    return ranked

def make_schedule(tasks, today, hours_per_day, start_hour):
    """
    Build a balanced daily plan. Each study task can be split into shorter sessions,
    urgent/difficult/important tasks score higher, and subjects rotate within a day.
    """
    pending = [dict(t) for t in tasks if t.get("Status", "Pending") != "Completed"]
    ranked = best_first_search(pending, today)
    if not pending:
        return [], ranked

    remaining = {id(task): max(0.0, float(task.get("Hours", 0))) for task in pending}
    ranked_by_id = {id(task): task for task in pending}
    max_due = max(
        max(0, ((task["Exam date"] if not isinstance(task["Exam date"], str)
                 else pd.to_datetime(task["Exam date"]).date()) - today).days)
        for task in pending
    )
    # Plan at least one week ahead, and extend beyond the latest exam when needed.
    planning_days = min(60, max(7, max_due + 1))
    sessions = []
    session_length = min(1.25, max(0.5, float(hours_per_day) / 3))
    subject_last_used = {}
    for day_offset in range(planning_days):
        day = today + timedelta(days=day_offset)
        capacity_left = float(hours_per_day)
        day_subjects = set()
        day_task_ids = set()
        while capacity_left >= 0.25:
            candidates = []
            for task in pending:
                task_id = id(task)
                hours_left = remaining.get(task_id, 0.0)
                if hours_left < 0.01 or task_id in day_task_ids:
                    continue
                due_date = task["Exam date"]
                if isinstance(due_date, str):
                    due_date = pd.to_datetime(due_date).date()
                days_left = (due_date - day).days
                urgency = 14 / (max(0, days_left) + 1)
                difficulty_score = DIFFICULTY.get(task.get("Difficulty", "Moderate"), 2) * 1.7
                importance_score = IMPORTANCE.get(task.get("Importance", "Normal"), 2) * 2.0
                # Increase priority if the remaining workload is becoming hard to fit before the exam.
                days_available = max(1, days_left + 1)
                pace_pressure = min(5.0, hours_left / days_available * 1.5)
                score = urgency + difficulty_score + importance_score + pace_pressure
                subject = str(task.get("Subject", "Other"))
                # Prefer different subjects within a day; rotate back to a subject later.
                if subject in day_subjects:
                    score -= 7.0
                last_day = subject_last_used.get(subject)
                if last_day is not None and (day - last_day).days == 1 and subject not in day_subjects:
                    score += 0.35
                candidates.append((score, task, due_date))
            if not candidates:
                break
            candidates.sort(key=lambda item: item[0], reverse=True)
            score, task, due_date = candidates[0]
            task_id = id(task)
            subject = str(task.get("Subject", "Other"))
            duration = min(session_length, capacity_left, remaining[task_id])
            if duration < 0.01:
                day_task_ids.add(task_id)
                continue
            start = datetime.combine(day, datetime.min.time()) + timedelta(
                hours=start_hour, minutes=int((float(hours_per_day) - capacity_left) * 60)
            )
            finish = start + timedelta(hours=duration)
            task_rank = next((r for r in ranked if r.get("Task") == task.get("Task")
                              and r.get("Subject") == task.get("Subject")), {})
            sessions.append({
                "Date": day, "Day": day.strftime("%A"),
                "Start": start.strftime("%I:%M %p"), "End": finish.strftime("%I:%M %p"),
                "Subject": subject, "Study task": task.get("Task", "Study session"),
                "Hours": round(duration, 2), "Importance": task.get("Importance", "Normal"),
                "Priority score": round(score, 2), "Exam date": due_date
            })
            remaining[task_id] -= duration
            capacity_left -= duration
            day_subjects.add(subject)
            day_task_ids.add(task_id)
            subject_last_used[subject] = day

        # Preserve unused capacity for future days; never force extra sessions just to fill the day.

    # If workload remains after the planning window, place it into subsequent days in a balanced rotation.
    day_offset = planning_days
    while any(value >= 0.01 for value in remaining.values()) and day_offset < 90:
        day = today + timedelta(days=day_offset)
        capacity_left = float(hours_per_day)
        day_subjects = set()
        day_task_ids = set()
        while capacity_left >= 0.25:
            choices = []
            for task in pending:
                task_id = id(task)
                if remaining.get(task_id, 0.0) < 0.01 or task_id in day_task_ids:
                    continue
                due_date = task["Exam date"]
                if isinstance(due_date, str):
                    due_date = pd.to_datetime(due_date).date()
                days_left = (due_date - day).days
                score = (14 / (max(0, days_left) + 1)
                         + DIFFICULTY.get(task.get("Difficulty", "Moderate"), 2) * 1.7
                         + IMPORTANCE.get(task.get("Importance", "Normal"), 2) * 2.0)
                if task.get("Subject") in day_subjects:
                    score -= 7
                choices.append((score, task, due_date))
            if not choices:
                break
            score, task, due_date = max(choices, key=lambda item: item[0])
            task_id = id(task)
            duration = min(session_length, capacity_left, remaining[task_id])
            start = datetime.combine(day, datetime.min.time()) + timedelta(
                hours=start_hour, minutes=int((float(hours_per_day) - capacity_left) * 60)
            )
            finish = start + timedelta(hours=duration)
            sessions.append({
                "Date": day, "Day": day.strftime("%A"),
                "Start": start.strftime("%I:%M %p"), "End": finish.strftime("%I:%M %p"),
                "Subject": str(task.get("Subject", "Other")), "Study task": task.get("Task", "Study session"),
                "Hours": round(duration, 2), "Importance": task.get("Importance", "Normal"),
                "Priority score": round(score, 2), "Exam date": due_date
            })
            remaining[task_id] -= duration
            capacity_left -= duration
            day_subjects.add(str(task.get("Subject", "Other")))
            day_task_ids.add(task_id)
            subject_last_used[str(task.get("Subject", "Other"))] = day
        day_offset += 1
    return sessions, ranked

def task_frame(tasks):
    frame = pd.DataFrame(tasks)
    if not frame.empty:
        frame["Exam date"] = pd.to_datetime(frame["Exam date"]).dt.date
    return frame

today = date.today()
if "tasks" not in st.session_state:
    st.session_state.tasks = demo_tasks(today)
if "generated" not in st.session_state:
    st.session_state.generated = False

st.markdown("""
<div class="hero">
  <div class="eyebrow">STUDYPILOT · YOUR EXAM SEASON COMMAND CENTRE</div>
  <h1>Big goals. Small sessions. You've got this.</h1>
  <p>Know exactly how many days are left, what deserves your attention, and what to study next. Your plan is prioritized using heuristic search from your AISC syllabus.</p>
</div>
""", unsafe_allow_html=True)

df = task_frame(st.session_state.tasks)
pending_df = df[df["Status"] != "Completed"] if not df.empty else df
pending_count = len(pending_df)
pending_hours = float(pending_df["Hours"].sum()) if not pending_df.empty else 0
completed_count = int((df["Status"] == "Completed").sum()) if not df.empty else 0
next_deadline = pending_df["Exam date"].min() if not pending_df.empty else None
days_to_exam = (next_deadline - today).days if next_deadline else None

m1, m2, m3, m4 = st.columns(4)
m1.metric("Pending tasks", pending_count)
m2.metric("Study hours left", f"{pending_hours:g} h")
m3.metric("Completed tasks", completed_count)
m4.metric("Next deadline", f"{days_to_exam} days" if days_to_exam is not None else "—",
          next_deadline.strftime("%d %b") if next_deadline else "No pending tasks")

# Student-friendly progress and exam countdowns, grouped by subject.
total_count = len(df)
completion_pct = int(round((completed_count / total_count) * 100)) if total_count else 0
st.markdown(f"""
<div class="progress-wrap">
  <div class="progress-title">Your semester progress <span style="float:right;color:#5264c9">{completion_pct}%</span></div>
  <div class="progress-sub">{completed_count} of {total_count} study tasks completed. Every focused session moves you forward.</div>
</div>
""", unsafe_allow_html=True)
st.progress(completion_pct / 100 if total_count else 0)

exam_dates = {}
for task in st.session_state.tasks:
    exam_day = task.get("Exam date", today)
    if isinstance(exam_day, str):
        exam_day = pd.to_datetime(exam_day).date()
    subject_name = str(task.get("Subject", "Subject"))
    if subject_name not in exam_dates or exam_day < exam_dates[subject_name]:
        exam_dates[subject_name] = exam_day
upcoming_exams = sorted(
    [(subject_name, exam_day, (exam_day - today).days)
     for subject_name, exam_day in exam_dates.items()],
    key=lambda item: item[1]
)
st.markdown("""
<div class="section-heading">
  <div>
    <div class="section-eyebrow">Countdowns</div>
    <h2 style="margin:0">Your exams, at a glance</h2>
  </div>
  <div class="section-caption">Stay ahead, one subject at a time</div>
</div>
""", unsafe_allow_html=True)
if upcoming_exams:
    exam_cols = st.columns(min(3, len(upcoming_exams)))
    for idx, (subject_name, exam_day, days_left) in enumerate(upcoming_exams[:3]):
        with exam_cols[idx]:
            if days_left < 0:
                big_text, tag, urgent = "Passed", "Check your next exam", False
            elif days_left == 0:
                big_text, tag, urgent = "Today!", "Final review mode", True
            elif days_left == 1:
                big_text, tag, urgent = "1 day", "Time to revise", True
            else:
                big_text, tag, urgent = f"{days_left} days", "You've got time — plan it", days_left <= 3
            st.markdown(f"""
            <div class="exam-card {'urgent' if urgent else ''}">
              <div class="exam-subject">{subject_name}</div>
              <div class="exam-days">{big_text}</div>
              <div class="exam-date">{exam_day.strftime('%a, %d %b %Y')}</div>
              <div class="exam-tag">{tag}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Add an exam date to see your countdown cards here.")


# Always-visible subject launcher: the five subjects requested for the student dashboard.
dashboard_subjects = [
    ("Artificial Intelligence and Cloud Computing", "AI concepts, search methods and cloud fundamentals", ["artificial intelligence", "cloud computing"]),
    ("Computer Networks", "Networking concepts, protocols and subnetting", ["computer networks"]),
    ("Software Engineering", "Requirements, design, testing and process models", ["software engineering"]),
    ("Game Theory", "Strategies, game trees and decision-making", ["game theory"]),
    ("Predictive Analysis", "Prediction, modelling and analytical methods", ["predictive analysis", "predictive analytics"]),
]
st.markdown("""
<div class="section-heading">
  <div>
    <div class="section-eyebrow">YOUR SUBJECTS</div>
    <h2 style="margin:0">What do you want to study?</h2>
  </div>
  <div class="section-caption">Choose a subject to see your progress</div>
</div>
""", unsafe_allow_html=True)
subject_rows = [st.columns(3), st.columns(2)]
for index, (subject_name, subject_desc, aliases) in enumerate(dashboard_subjects):
    col = subject_rows[0][index] if index < 3 else subject_rows[1][index - 3]
    related = []
    for task_item in st.session_state.tasks:
        current_subject = str(task_item.get("Subject", "")).lower()
        if any(alias in current_subject for alias in aliases):
            related.append(task_item)
    open_count = sum(1 for task_item in related if task_item.get("Status", "Pending") != "Completed")
    done_count = sum(1 for task_item in related if task_item.get("Status") == "Completed")
    with col:
        st.markdown(f"**{index + 1:02d}  {subject_name}**")
        st.caption(subject_desc)
        st.markdown(f"**{open_count}** tasks left · **{done_count}** completed")
        if st.button("Plan this subject", key=f"subject_launch_{index}", use_container_width=True):
            st.session_state.chosen_dashboard_subject = subject_name
            st.session_state["subject_option"] = subject_name
            st.session_state["handout_subject_prefill"] = subject_name
            st.session_state["show_subject_plan_hint"] = True
            st.rerun()
        st.divider()
if st.session_state.get("show_subject_plan_hint"):
    st.info("Selected: " + st.session_state.get("chosen_dashboard_subject", "") + ". Open **Build from handout** to upload its course handout and generate a topic-based plan.")

with st.sidebar:
    st.image("assets/studypilot-logo.svg", use_container_width=True)
    st.caption("Your personal exam-prep workspace.")
    st.divider()
    st.markdown("### Schedule settings")
    hours_per_day = st.slider("Daily study capacity", 1.0, 10.0, 4.0, 0.5)
    start_hour = st.selectbox("Start time", list(range(6, 21)), index=9,
        format_func=lambda hour: datetime.strptime(str(hour), "%H").strftime("%I:%M %p"))
    horizon = st.slider("Days to show", 3, 21, 7)
    st.divider()
    if st.button("Restore demo tasks", use_container_width=True):
        st.session_state.tasks = demo_tasks(date.today())
        st.session_state.generated = False
        st.rerun()
    if st.button("Clear all tasks", use_container_width=True):
        st.session_state.tasks = []
        st.session_state.generated = False
        st.rerun()
    st.caption("Demo data is included so you can present the project immediately.")

plan_tab, tasks_tab, syllabus_tab, algorithm_tab = st.tabs(["Study plan", "Manage tasks", "Build from handout", "Algorithm"])

with plan_tab:
    st.markdown("## Today's game plan")
    st.caption("Small, focused sessions beat last-minute cramming. Your highest-priority task comes first.")
    controls = st.columns([1, 2])
    with controls[0]:
        if st.button("Generate study plan", type="primary", use_container_width=True):
            st.session_state.generated = True
    with controls[1]:
        st.caption("Adjust your daily capacity and start time in the sidebar.")
    sessions, ranked = make_schedule(st.session_state.tasks, today, hours_per_day, start_hour)
    if not st.session_state.generated:
        st.info("Your demo tasks are loaded. Select **Generate study plan** to build the timetable.")
    if not sessions:
        st.warning("No pending tasks. Add a task in Manage tasks or restore the demo tasks.")
    else:
        schedule_df = pd.DataFrame(sessions)
        schedule_df = schedule_df[pd.to_datetime(schedule_df["Date"]) <= pd.Timestamp(today + timedelta(days=horizon - 1))]
        if st.session_state.generated:
            st.success(f"Plan generated successfully · {len(schedule_df)} session blocks shown.")
        if schedule_df.empty:
            st.info("No study sessions fall within this date range. Increase Days to show.")
        else:
            for session_day in sorted(schedule_df["Date"].unique()):
                day_items = schedule_df[schedule_df["Date"] == session_day]
                st.markdown(f"### {session_day.strftime('%A, %d %B')}")
                st.caption(f"{day_items['Hours'].sum():g} hours planned")
                for _, item in day_items.iterrows():
                    st.markdown(f"""
                    <div class="task-card">
                      <div class="task-time">{item["Start"]} – {item["End"]} &nbsp; · &nbsp; {item["Hours"]:g} hours</div>
                      <div class="task-title">{item["Study task"]}</div>
                      <div class="task-meta">{item["Subject"]} &nbsp; · &nbsp; {item["Importance"]} priority</div>
                    </div>
                    """, unsafe_allow_html=True)
            with st.expander("View timetable as a table"):
                st.dataframe(schedule_df, use_container_width=True, hide_index=True)
            st.download_button("Download timetable as CSV", schedule_df.to_csv(index=False).encode("utf-8"),
                               "studypilot_schedule.csv", "text/csv")
            st.markdown("### Study time by subject")
            st.bar_chart(schedule_df.groupby("Subject")["Hours"].sum().sort_values(ascending=False))
        if ranked:
            with st.expander("View heuristic priority ranking"):
                st.dataframe(pd.DataFrame(ranked)[["Subject", "Task", "Exam date", "Difficulty", "Importance", "Priority score"]],
                             use_container_width=True, hide_index=True)

with tasks_tab:
    st.markdown("## Manage your tasks")
    st.caption("Add a study goal, then edit task details or mark tasks completed below.")
    with st.form("add_task", clear_on_submit=True):
        left, right = st.columns(2)
        subject = left.text_input("Subject", placeholder="Artificial Intelligence")
        task_name = right.text_input("Task name", placeholder="Revise Best-First Search")
        c1, c2, c3 = st.columns(3)
        due_date = c1.date_input("Exam / deadline", value=today + timedelta(days=4))
        hours = c2.number_input("Estimated hours", min_value=0.25, max_value=100.0, value=1.5, step=0.25)
        difficulty = c3.selectbox("Difficulty", list(DIFFICULTY), index=1)
        c4, c5 = st.columns(2)
        importance = c4.selectbox("Importance", list(IMPORTANCE), index=1)
        notes = c5.text_input("Notes (optional)")
        add = st.form_submit_button("Add task", type="primary")
        if add:
            if not subject.strip() or not task_name.strip():
                st.error("Please enter both a subject and a task name.")
            else:
                st.session_state.tasks.append({"Subject":subject.strip(), "Task":task_name.strip(),
                    "Exam date":due_date, "Hours":float(hours), "Difficulty":difficulty, "Importance":importance,
                    "Status":"Pending", "Notes":notes.strip()})
                st.session_state.generated = False
                st.rerun()
    if st.session_state.tasks:
        st.markdown("### Existing tasks")
        edited = st.data_editor(task_frame(st.session_state.tasks), use_container_width=True, hide_index=True,
            num_rows="dynamic", key="tasks_editor",
            column_config={
                "Exam date":st.column_config.DateColumn(format="DD MMM YYYY"),
                "Hours":st.column_config.NumberColumn(min_value=0.25, step=0.25, format="%.2f h"),
                "Difficulty":st.column_config.SelectboxColumn(options=list(DIFFICULTY)),
                "Importance":st.column_config.SelectboxColumn(options=list(IMPORTANCE)),
                "Status":st.column_config.SelectboxColumn(options=["Pending", "Completed"])
            })
        if st.button("Save task changes", type="primary"):
            edited["Exam date"] = pd.to_datetime(edited["Exam date"]).dt.date
            st.session_state.tasks = edited.fillna("").to_dict("records")
            st.session_state.generated = False
            st.rerun()
    else:
        st.info("No tasks yet. Add one above or restore the demo tasks in the sidebar.")

with syllabus_tab:
    st.markdown("## Build a study plan from your course handout")
    st.caption("Choose a subject and upload the syllabus. StudyPilot extracts topics for you to review before adding them to your plan.")
    with st.form("handout_setup"):
        subject_options = ["Artificial Intelligence and Cloud Computing", "Computer Networks", "Software Engineering", "Game Theory", "Predictive Analysis", "Other / custom subject"]
        default_subject = st.session_state.get("handout_subject_prefill", "Artificial Intelligence and Cloud Computing")
        default_index = subject_options.index(default_subject) if default_subject in subject_options else 0
        subject_option = st.selectbox("Choose subject", subject_options, index=default_index, key="subject_option")
        custom_subject = st.text_input("Enter subject name", placeholder="Type your subject here") if subject_option == "Other / custom subject" else ""
        subject_choice = custom_subject.strip() if subject_option == "Other / custom subject" else subject_option
        handout = st.file_uploader("Upload course handout", type=["pdf", "docx", "txt"], help="PDF, Word document (.docx), or plain text.")
        exam_day = st.date_input("Exam date", value=today + timedelta(days=7), key="handout_exam_day")
        default_hours = st.number_input("Estimated hours per topic", min_value=0.25, max_value=8.0, value=1.0, step=0.25)
        parse_handout = st.form_submit_button("Extract topics", type="primary")
    if parse_handout:
        if not subject_choice.strip():
            st.error("Enter the subject name first.")
        elif handout is None:
            st.error("Upload a course handout to extract topics.")
        else:
            try:
                extracted_text, extracted_topics = extract_topics(handout)
                st.session_state.handout_subject = subject_choice.strip()
                st.session_state.extracted_exam_day = exam_day
                st.session_state.handout_hours = float(default_hours)
                st.session_state.extracted_topics = extracted_topics
                st.session_state.handout_filename = handout.name
                st.session_state.handout_text_preview = extracted_text[:12000]
                st.session_state.selected_topics = extracted_topics[:]
                if not extracted_topics:
                    st.warning("The file text was read, but no clear topic headings were detected. Try a text-based PDF or DOCX, or review the extracted text below.")
                else:
                    st.success("Extracted " + str(len(extracted_topics)) + " possible topics from " + handout.name + ". Review the list before adding it to your plan.")
            except Exception as exc:
                st.error("Could not read this file: " + str(exc))
    if st.session_state.get("extracted_topics"):
        st.markdown("### Review the extracted topics")
        st.caption("The extraction is based on headings, numbered items, and bullet points. Check the topics before adding them.")
        selected = st.multiselect("Topics to include", options=st.session_state.extracted_topics,
                                  default=st.session_state.get("selected_topics", st.session_state.extracted_topics),
                                  key="topics_multiselect")
        topic_cols = st.columns(3)
        with topic_cols[0]:
            per_topic_hours = st.number_input("Hours per selected topic", min_value=0.25, max_value=8.0,
                                              value=float(st.session_state.get("handout_hours", 1.0)), step=0.25, key="topic_hours")
        with topic_cols[1]:
            topic_importance = st.selectbox("Default importance", list(IMPORTANCE), index=2, key="topic_importance")
        with topic_cols[2]:
            topic_difficulty = st.selectbox("Default difficulty", list(DIFFICULTY), index=1, key="topic_difficulty")
        st.info("Selected " + str(len(selected)) + " topics · estimated workload " + str(round(len(selected) * per_topic_hours, 2)) + " hours")
        if st.button("Add selected topics to my study plan", type="primary", use_container_width=True):
            existing = {(str(t.get("Subject", "")).lower(), str(t.get("Task", "")).lower()) for t in st.session_state.tasks}
            added = 0
            for topic in selected:
                key = (st.session_state.handout_subject.lower(), topic.lower())
                if key in existing:
                    continue
                st.session_state.tasks.append({"Subject":st.session_state.handout_subject, "Task":topic,
                    "Exam date":st.session_state.extracted_exam_day, "Hours":float(per_topic_hours),
                    "Difficulty":topic_difficulty, "Importance":topic_importance, "Status":"Pending",
                    "Notes":"Extracted from " + st.session_state.get("handout_filename", "course handout")})
                existing.add(key)
                added += 1
            st.session_state.generated = False
            st.success("Added " + str(added) + " topic tasks to your planner. Open Study plan and generate your schedule.")
    elif st.session_state.get("handout_text_preview"):
        with st.expander("Preview extracted text"):
            st.text(st.session_state.handout_text_preview)
    st.caption("Tip: scanned PDFs that contain only images may not have selectable text. OCR is not included in this version.")
with algorithm_tab:
    st.markdown("## How the algorithm works")
    st.write("This project uses Greedy Best-First Search, a heuristic search technique listed in the AISC syllabus. Each pending study task receives a score, and the task with the highest score is selected first.")
    st.latex(r"h(n)=\frac{10}{d+1}+1.4D+1.8I+0.25\min(H,3)")
    st.markdown("### Heuristic factors")
    st.markdown("""
- **Urgency (d):** fewer days until the exam gives a higher score.
- **Difficulty (D):** Easy = 1, Moderate = 2, Hard = 3, Very hard = 4.
- **Importance (I):** Low = 1, Normal = 2, High = 3, Critical = 4.
- **Workload (H):** estimated study hours, capped at 3 for this score.
""")
    st.markdown("### Search process")
    st.markdown("""
1. Treat each pending topic as a state and calculate its heuristic score.
2. Prioritise topics using exam urgency, difficulty, importance, and remaining workload.
3. Split long topics into focused sessions instead of filling a whole day with one topic.
4. Rotate across subjects within each day when possible, while keeping approaching exams and difficult topics high priority.
5. Respect the selected daily study capacity and schedule remaining work into later days.
""")
    st.info("Greedy Best-First Search is simple and explainable, but it does not guarantee a globally optimal timetable. The balancing and session-splitting rules are scheduling heuristics layered on top of the search ranking. Tasks are stored in session state in this demo, not a permanent database.")

st.divider()
st.caption("StudyPilot · Artificial Intelligence and Soft Computing · Heuristic Search course project")
