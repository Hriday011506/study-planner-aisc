import heapq
import itertools
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="StudyPilot | Smart Study Planner", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#17233b; --muted:#718096; --line:#e6eaf1; --accent:#4f5fc9; }
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:#f7f8fb;color:var(--ink);}
.block-container {max-width:1180px;padding:1.55rem 2rem 3rem;}
h1,h2,h3 {font-family:'Manrope',sans-serif;letter-spacing:-.45px;color:#17233b;}
[data-testid="stSidebar"] {background:#fff;border-right:1px solid var(--line);}
[data-testid="stSidebar"] > div {padding-top:1.3rem;}
[data-testid="stMetric"] {background:#fff;border:1px solid var(--line);border-radius:13px;padding:15px 17px;box-shadow:none;}
[data-testid="stMetricLabel"] {color:#778198;font-size:.82rem;}
[data-testid="stMetricValue"] {color:#172b53;font-family:'Manrope',sans-serif;font-weight:800;}
div[data-testid="stTabs"] button {font-weight:700;}
.stButton>button,.stDownloadButton>button {border-radius:9px;font-weight:700;min-height:2.5rem;}
.stButton>button[kind="primary"] {background:#4f5fc9;border-color:#4f5fc9;}
.stButton>button[kind="primary"]:hover {background:#414fae;border-color:#414fae;}
div[data-testid="stForm"] {background:white;border:1px solid var(--line);border-radius:13px;padding:18px;}
div[data-testid="stDataFrame"],div[data-testid="stTable"] {border:1px solid var(--line);border-radius:9px;overflow:hidden;}
hr {border-color:var(--line);}
.hero {padding:8px 0 22px;border-bottom:1px solid var(--line);margin-bottom:22px;}
.hero .eyebrow {font-size:.72rem;letter-spacing:1.6px;text-transform:uppercase;font-weight:800;color:var(--accent);margin-bottom:9px;}
.hero h1 {font-family:'Manrope',sans-serif;font-size:2.2rem;line-height:1.12;margin:0;color:#17233b;font-weight:800;}
.hero p {font-size:1rem;color:#68758c;margin:.65rem 0 0;max-width:710px;}
.panel {background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px;margin:0 0 10px;}
.panel-title {font-weight:800;color:#1e2d4b;font-size:.98rem;margin-bottom:4px;}
.panel-sub {font-size:.83rem;color:#778198;}
.score {display:inline-block;background:#eef0ff;color:#424fb3;border-radius:6px;padding:4px 7px;font-size:.75rem;font-weight:800;}
.callout {border-left:3px solid #6472d3;background:#f0f2ff;padding:11px 13px;border-radius:0 8px 8px 0;color:#38456b;font-size:.9rem;}
div[data-testid="stAlert"] {border-radius:9px;}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

IMPORTANCE = {"Low": 1, "Normal": 2, "High": 3, "Critical": 4}
DIFFICULTY = {"Easy": 1, "Moderate": 2, "Hard": 3, "Very hard": 4}

def demo_tasks(today):
    return [
        {"Subject":"Computer Networks","Task":"Subnetting practice","Exam date":today+timedelta(days=2),"Hours":2.0,"Difficulty":"Hard","Importance":"Critical","Status":"Pending","Notes":"Practice VLSM and CIDR"},
        {"Subject":"Artificial Intelligence","Task":"Heuristic search revision","Exam date":today+timedelta(days=3),"Hours":1.5,"Difficulty":"Moderate","Importance":"High","Status":"Pending","Notes":"A*, Best-First Search, hill climbing"},
        {"Subject":"Artificial Intelligence","Task":"State-space problem practice","Exam date":today+timedelta(days=3),"Hours":1.0,"Difficulty":"Moderate","Importance":"High","Status":"Pending","Notes":"Trace states and solution paths"},
        {"Subject":"Software Engineering","Task":"UML diagrams","Exam date":today+timedelta(days=5),"Hours":1.5,"Difficulty":"Moderate","Importance":"Normal","Status":"Pending","Notes":"Use-case, activity, sequence"},
        {"Subject":"Computer Networks","Task":"TCP and congestion control","Exam date":today+timedelta(days=2),"Hours":1.0,"Difficulty":"Moderate","Importance":"High","Status":"Pending","Notes":"Slow start and AIMD"},
        {"Subject":"Cloud Computing","Task":"Service and deployment models","Exam date":today+timedelta(days=7),"Hours":1.5,"Difficulty":"Moderate","Importance":"Normal","Status":"Pending","Notes":"IaaS, PaaS, SaaS"},
        {"Subject":"Artificial Intelligence","Task":"Practice questions","Exam date":today+timedelta(days=3),"Hours":1.0,"Difficulty":"Easy","Importance":"Normal","Status":"Pending","Notes":"Attempt before checking solutions"},
    ]

def score(task, today):
    days = max(0, (task["Exam date"]-today).days)
    urgency = 10/(days+1)
    difficulty = DIFFICULTY.get(task["Difficulty"], 2)*1.4
    importance = IMPORTANCE.get(task["Importance"], 2)*1.8
    workload = min(float(task["Hours"]), 3)*0.25
    return round(urgency+difficulty+importance+workload, 2)

def best_first_search(tasks, today):
    # Greedy Best-First Search: explore the pending task with the highest heuristic first.
    queue, counter = [], itertools.count()
    for task in tasks:
        heapq.heappush(queue, (-score(task, today), next(counter), task))
    ranked, expanded = [], 0
    while queue:
        neg_score, _, task = heapq.heappop(queue)
        ranked.append({**task, "Priority score":round(-neg_score,2),
                       "Days left":max(0,(task["Exam date"]-today).days)})
        expanded += 1
    return ranked, expanded

def make_schedule(tasks, today, hours_per_day, start_hour):
    ranked, expanded = best_first_search([t for t in tasks if t["Status"]!="Completed"], today)
    usage, sessions = {}, []
    for task in ranked:
        remaining = float(task["Hours"])
        while remaining > 0.001:
            day = today
            while usage.get(day,0) >= hours_per_day-0.001:
                day += timedelta(days=1)
                if (day-today).days > 30:
                    break
            if (day-today).days > 30:
                break
            free = hours_per_day-usage.get(day,0)
            duration = min(remaining,free)
            start = datetime.combine(day,datetime.min.time()) + timedelta(hours=start_hour,minutes=int(usage.get(day,0)*60))
            end = start+timedelta(hours=duration)
            usage[day] = usage.get(day,0)+duration
            sessions.append({"Date":day,"Day":day.strftime("%A"),"Start":start.strftime("%I:%M %p"),
             "End":end.strftime("%I:%M %p"),"Subject":task["Subject"],"Study task":task["Task"],
             "Hours":round(duration,2),"Importance":task["Importance"],"Priority score":task["Priority score"]})
            remaining -= duration
    return sessions, ranked, expanded

def frame_tasks(tasks):
    df = pd.DataFrame(tasks)
    if not df.empty:
        df["Exam date"] = pd.to_datetime(df["Exam date"]).dt.date
    return df

today = date.today()
if "tasks" not in st.session_state:
    st.session_state.tasks = demo_tasks(today)
if "generated" not in st.session_state:
    st.session_state.generated = False

st.markdown("""
<div class="hero">
  <div class="eyebrow">STUDYPILOT / INTELLIGENT STUDY PLANNING</div>
  <h1>Study smarter, one session at a time.</h1>
  <p>Turn upcoming exams and assignments into a clear study schedule, guided by heuristic search from your AISC syllabus.</p>
</div>""", unsafe_allow_html=True)

df = frame_tasks(st.session_state.tasks)
pending = df[df["Status"]!="Completed"] if not df.empty else df
next_exam = pending["Exam date"].min() if not pending.empty else None
metrics = [
 ("Pending tasks",str(len(pending)),"Study goals still to do"),
 ("Hours remaining",f'{pending["Hours"].sum():g}h' if not pending.empty else "0h","Estimated workload"),
 ("Completed tasks",str((df["Status"]=="Completed").sum()) if not df.empty else "0","Keep up the momentum"),
 ("Next exam",f'{(next_exam-today).days} days' if next_exam else "—",next_exam.strftime("%d %b") if next_exam else "No pending exams"),
]
cols = st.columns(4)
for c,(label,value,note) in zip(cols,metrics):
    c.markdown(f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div><div class="note">{note}</div></div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🎓 StudyPilot")
    st.caption("Plan with purpose. Learn with confidence.")
    st.divider()
    st.markdown("### Planning preferences")
    hours_per_day = st.slider("Study capacity per day",1.0,10.0,4.0,0.5)
    start_hour = st.selectbox("Preferred start time",list(range(6,21)),index=9,format_func=lambda h:datetime.strptime(str(h),"%H").strftime("%I:00 %p"))
    horizon = st.slider("Schedule view",3,21,7)
    st.caption("Priority = urgency + difficulty + importance + workload.")
    st.divider()
    if st.button("↻ Restore sample tasks",use_container_width=True):
        st.session_state.tasks = demo_tasks(date.today())
        st.session_state.generated = False
        st.rerun()
    if st.button("🗑 Clear all tasks",use_container_width=True):
        st.session_state.tasks = []
        st.session_state.generated = False
        st.rerun()

plan_tab, tasks_tab, ai_tab = st.tabs(["🗓️ Smart study plan","📚 Manage tasks","🧠 How the AI works"])
with plan_tab:
    head, button = st.columns([1.6,1])
    head.markdown("### Your schedule")
    head.caption("Tasks are ranked by the heuristic score before being placed into daily study capacity.")
    if button.button("✨ Generate plan",type="primary",use_container_width=True):
        st.session_state.generated = True
    if not st.session_state.generated:
        st.info("Demo tasks are loaded. Click **Generate smart plan** to create your first timetable.")
    sessions, ranked, expanded = make_schedule(st.session_state.tasks,date.today(),hours_per_day,start_hour)
    if sessions:
        sdf = pd.DataFrame(sessions)
        sdf = sdf[pd.to_datetime(sdf["Date"]) <= pd.Timestamp(today+timedelta(days=horizon-1))]
        if st.session_state.generated:
            st.success(f"Plan generated by Greedy Best-First Search · {len(sdf)} session(s) in the selected horizon.")
        if not sdf.empty:
            days = sorted(sdf["Date"].unique())
            for row_start in range(0,len(days),3):
                day_cols = st.columns(min(3,len(days)-row_start))
                for col,day in zip(day_cols,days[row_start:row_start+3]):
                    daily = sdf[sdf["Date"]==day]
                    with col:
                        st.markdown(f"**{day.strftime('%a, %d %b')}**")
                        st.caption(f'{daily["Hours"].sum():g} study hours')
                        for _,item in daily.iterrows():
                            st.markdown(f'<div class="panel"><div style="font-size:.75rem;color:#7b849a;font-weight:700">{item["Start"]} – {item["End"]}</div><div class="panel-title" style="margin-top:6px">{item["Study task"]}</div><div class="panel-sub">{item["Subject"]}</div><div style="margin-top:9px"><span class="score">{item["Hours"]}h</span><span style="font-size:.75rem;color:#6e7890;margin-left:6px">{item["Importance"]} priority</span></div></div>',unsafe_allow_html=True)
            with st.expander("View complete timetable and priority scores"):
                st.dataframe(sdf,use_container_width=True,hide_index=True)
            st.download_button("⬇️ Download timetable (CSV)",sdf.to_csv(index=False).encode("utf-8"),"studypilot_schedule.csv","text/csv")
            st.markdown("#### Workload by subject")
            st.bar_chart(sdf.groupby("Subject")["Hours"].sum().sort_values(ascending=False))
    elif pending.empty:
        st.warning("There are no pending tasks. Add a task in Manage tasks or restore demo tasks.")
    if ranked and st.session_state.generated:
        with st.expander("See AI priority ranking"):
            st.dataframe(pd.DataFrame(ranked)[["Subject","Task","Exam date","Difficulty","Importance","Hours","Priority score"]],use_container_width=True,hide_index=True)

with tasks_tab:
    st.markdown("### Add a task")
    with st.form("add_task",clear_on_submit=True):
        a,b = st.columns(2)
        subject = a.text_input("Subject",placeholder="e.g. Artificial Intelligence")
        task = b.text_input("Study task",placeholder="e.g. Revise A* search")
        c,d,e = st.columns(3)
        due = c.date_input("Exam / deadline",value=today+timedelta(days=4))
        hours = d.number_input("Estimated hours",min_value=0.25,max_value=100.0,value=1.5,step=0.25)
        difficulty = e.selectbox("Difficulty",list(DIFFICULTY),index=1)
        f,g = st.columns(2)
        importance = f.selectbox("Importance",list(IMPORTANCE),index=1)
        notes = g.text_input("Notes (optional)")
        submitted = st.form_submit_button("＋ Add task",type="primary")
        if submitted:
            if not subject.strip() or not task.strip():
                st.error("Please enter both a subject and a task.")
            else:
                st.session_state.tasks.append({"Subject":subject.strip(),"Task":task.strip(),"Exam date":due,
                "Hours":float(hours),"Difficulty":difficulty,"Importance":importance,"Status":"Pending","Notes":notes.strip()})
                st.session_state.generated = False
                st.success("Task added.")
                st.rerun()
    if st.session_state.tasks:
        editable = st.data_editor(frame_tasks(st.session_state.tasks),use_container_width=True,hide_index=True,num_rows="dynamic",
          column_config={"Exam date":st.column_config.DateColumn(format="DD MMM YYYY"),
           "Hours":st.column_config.NumberColumn(min_value=.25,step=.25,format="%.2f h"),
           "Difficulty":st.column_config.SelectboxColumn(options=list(DIFFICULTY)),
           "Importance":st.column_config.SelectboxColumn(options=list(IMPORTANCE)),
           "Status":st.column_config.SelectboxColumn(options=["Pending","Completed"])},key="editor")
        if st.button("💾 Save changes",type="primary"):
            editable["Exam date"] = pd.to_datetime(editable["Exam date"]).dt.date
            st.session_state.tasks = editable.fillna("").to_dict("records")
            st.session_state.generated = False
            st.success("Task list saved.")
            st.rerun()
    else:
        st.info("No tasks yet — add one above or restore the demo data in the sidebar.")

with ai_tab:
    st.markdown("### Heuristic search, explained")
    st.write("Each pending study task is represented as a state. The heuristic estimates how urgently the task should be considered, and a priority queue selects the highest-scoring task first.")
    st.latex(r"h(n)=\frac{10}{d+1}+1.4D+1.8I+0.25\min(H,3)")
    st.markdown("""
**Heuristic components**
- **Urgency:** 10 divided by (days until deadline + 1). A nearer exam scores higher.
- **Difficulty:** Easy = 1, Moderate = 2, Hard = 3, Very hard = 4.
- **Importance:** Low = 1, Normal = 2, High = 3, Critical = 4.
- **Workload:** A small tie-breaker based on estimated study hours.

**How search works**
1. Put all pending tasks in a priority queue.
2. Calculate the heuristic score for every task.
3. Remove the highest-scoring task from the queue.
4. Add it to the ranking and repeat until the queue is empty.
5. Pack ranked tasks into the available daily study hours.

**Important limitation:** Greedy Best-First Search is fast and explainable, but it does not guarantee a globally optimal timetable. This demo keeps tasks in browser session state; persistent multi-user storage could be added using a database.

**Cloud component:** Streamlit Community Cloud can host this app from the GitHub repository. The app requires no API keys.
""")
    if ranked:
        st.markdown("#### Live heuristic score examples")
        st.dataframe(pd.DataFrame(ranked)[["Subject","Task","Days left","Difficulty","Importance","Priority score"]],use_container_width=True,hide_index=True)

st.divider()
st.markdown("<div style='text-align:center;color:#8791a6;font-size:.8rem'>StudyPilot · Artificial Intelligence and Soft Computing · Heuristic Search project</div>",unsafe_allow_html=True)
