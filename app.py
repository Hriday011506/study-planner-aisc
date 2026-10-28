import heapq
import itertools
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="StudyPilot", page_icon="S", layout="wide", initial_sidebar_state="expanded")

# Use Streamlit-native components for reliable contrast and responsive rendering.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { color-scheme: light; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:#f5f7fb; color:#18243b; }
.block-container { max-width:1180px; padding:1.5rem 2rem 3rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; color:#18243b !important; letter-spacing:-.4px; }
p, label, .stMarkdown, [data-testid="stWidgetLabel"] { color:#263550; }
[data-testid="stSidebar"] { background:#ffffff; border-right:1px solid #e2e7f0; }
[data-testid="stSidebar"] * { color:#263550; }
[data-testid="stMetric"] { background:#ffffff; border:1px solid #e1e6f0; border-radius:14px; padding:16px; }
[data-testid="stMetricLabel"] { color:#5c6880 !important; }
[data-testid="stMetricValue"] { color:#182b50 !important; font-weight:800; }
[data-testid="stTabs"] button { font-weight:700; color:#43516a; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#4053bd; }
.stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button { border-radius:9px; font-weight:700; min-height:2.6rem; }
.stButton button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] { background:#485bc4; border-color:#485bc4; color:#ffffff; }
div[data-testid="stForm"] { background:#ffffff; border:1px solid #e1e6f0; border-radius:14px; padding:18px; }
div[data-testid="stDataFrame"] { background:#ffffff; border:1px solid #e1e6f0; border-radius:10px; }
hr { border-color:#e1e6f0; }
.hero { background:#eaf0ff; border:1px solid #d8e2ff; border-radius:18px; padding:26px 28px; margin-bottom:22px; }
.hero .eyebrow { color:#4053bd; font-size:.72rem; font-weight:800; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:8px; }
.hero h1 { font-size:2rem; line-height:1.18; margin:0; color:#172747 !important; }
.hero p { color:#40506c; font-size:.98rem; margin:.65rem 0 0; max-width:760px; line-height:1.55; }
.task-card { background:#ffffff; border:1px solid #e1e6f0; border-radius:12px; padding:14px 16px; margin-bottom:10px; }
.task-time { color:#52617a; font-size:.82rem; font-weight:700; }
.task-title { color:#182b50; font-size:1rem; font-weight:800; margin:5px 0; }
.task-meta { color:#52617a; font-size:.86rem; }
.small-label { color:#68758e; font-size:.75rem; font-weight:800; letter-spacing:1.2px; text-transform:uppercase; }
div[data-testid="stAlert"] { border-radius:10px; }
@media (max-width: 800px) {
 .block-container { padding:1rem .8rem 2rem; }
 .hero { padding:20px; }
 .hero h1 { font-size:1.55rem; }
}
</style>
""", unsafe_allow_html=True)

IMPORTANCE = {"Low": 1, "Normal": 2, "High": 3, "Critical": 4}
DIFFICULTY = {"Easy": 1, "Moderate": 2, "Hard": 3, "Very hard": 4}

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
    pending = [t for t in tasks if t.get("Status", "Pending") != "Completed"]
    ranked = best_first_search(pending, today)
    used, sessions = {}, []
    for task in ranked:
        remaining = float(task["Hours"])
        while remaining > 0.001:
            day = today
            while used.get(day, 0) >= hours_per_day - 0.001:
                day += timedelta(days=1)
                if (day - today).days > 30:
                    break
            if (day - today).days > 30:
                break
            offset = used.get(day, 0)
            duration = min(remaining, hours_per_day - offset)
            start = datetime.combine(day, datetime.min.time()) + timedelta(hours=start_hour, minutes=int(offset * 60))
            end = start + timedelta(hours=duration)
            used[day] = offset + duration
            sessions.append({"Date":day, "Day":day.strftime("%A"), "Start":start.strftime("%I:%M %p"),
                "End":end.strftime("%I:%M %p"), "Subject":task["Subject"], "Study task":task["Task"],
                "Hours":round(duration, 2), "Importance":task["Importance"], "Priority score":task["Priority score"]})
            remaining -= duration
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
  <div class="eyebrow">STUDYPILOT · SMART STUDY PLANNING</div>
  <h1>Your study plan, clear and under control.</h1>
  <p>Prioritize exams and assignments with a practical timetable powered by Greedy Best-First Search, a heuristic search technique from your AISC syllabus.</p>
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

with st.sidebar:
    st.markdown("## StudyPilot")
    st.caption("A focused workspace for exam preparation.")
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

plan_tab, tasks_tab, algorithm_tab = st.tabs(["Study plan", "Manage tasks", "Algorithm"])

with plan_tab:
    st.markdown("## Your study schedule")
    st.caption("Tasks with the highest heuristic priority are scheduled first.")
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
1. Treat each pending task as a state.
2. Calculate its heuristic score.
3. Put tasks into a priority queue.
4. Select the task with the highest score and repeat until all tasks are ranked.
5. Place ranked tasks into daily sessions without exceeding the chosen daily study capacity.
""")
    st.info("Greedy Best-First Search is simple and explainable, but it does not guarantee a globally optimal timetable. Tasks are stored in session state in this demo, not a permanent database.")

st.divider()
st.caption("StudyPilot · Artificial Intelligence and Soft Computing · Heuristic Search course project")
