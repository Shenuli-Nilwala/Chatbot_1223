import streamlit as st
import random
import datetime
import pandas as pd

st.set_page_config(page_title="Smart Study Planner", layout="wide")
st.title("🎓 Smart Study Planner")
st.caption("Optimized weekly schedule based on your user group and availability")

# -------------------------
# 1️⃣ Select User Group
# -------------------------
user_type = st.selectbox(
    "Select your group",
    ["Student", "Worker", "PhD/Researcher", "Other"]
)

# -------------------------
# 2️⃣ Subject Setup (Sidebar)
# -------------------------
st.sidebar.header("📚 Subjects & Exam Dates")
subjects = st.sidebar.text_input(
    "Enter subjects (comma separated)",
    placeholder="Programming, Economics, Marketing"
)

importance = {}
exam_dates = {}

if subjects:
    subject_list = [s.strip() for s in subjects.split(",")]

    st.sidebar.subheader("Importance (0-100)")
    for i, subject in enumerate(subject_list):
        importance[subject] = st.sidebar.slider(
            subject, 0, 100, 50, key=f"imp_{i}"
        )

    st.sidebar.subheader("📅 Exam Dates")
    for i, subject in enumerate(subject_list):
        exam_dates[subject] = st.sidebar.date_input(
            f"{subject} exam date", datetime.date.today(), key=f"exam_{i}"
        )

# -------------------------
# 3️⃣ Study Days
# -------------------------
st.header("Select Study Days")
days = st.multiselect(
    "Which days will you study?",
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    default=["Monday","Tuesday","Wednesday","Thursday","Friday"]
)

# -------------------------
# 4️⃣ Define Available Slots
# -------------------------
all_slots = [f"{str(i).zfill(2)}:00 - {str(i+1).zfill(2)}:00" for i in range(24)]

if user_type == "Student":
    available_slots = [s for s in all_slots if int(s[:2]) < 8 or int(s[:2]) >= 17]
elif user_type == "Worker":
    available_slots = [s for s in all_slots if int(s[:2]) < 8 or int(s[:2]) >= 15]
elif user_type == "PhD/Researcher":
    available_slots = all_slots
elif user_type == "Other":
    unavailable = st.multiselect(
        "Select unavailable hours", all_slots, key="other_unavailable"
    )
    available_slots = [s for s in all_slots if s not in unavailable]

# -------------------------
# 5️⃣ Select Preferred Hours per Day
# -------------------------
st.header("Select Available Hours per Day")
day_time_slots = {}
cols = st.columns(2)

for i, day in enumerate(days):
    with cols[i % 2]:
        with st.expander(f"{day} study hours"):
            day_time_slots[day] = st.multiselect(
                "Select hours",
                available_slots,
                default=available_slots[:4],
                key=f"hours_{day}"  # unique key per day
            )
            if day_time_slots[day]:
                st.caption(f"{len(day_time_slots[day])} hours selected")

# -------------------------
# 6️⃣ Study Mode
# -------------------------
st.header("Study Mode")
study_mode = st.radio(
    "Choose study method",
    ["Normal Study", "Pomodoro (break every 4 sessions)"],
    key="study_mode"
)

# -------------------------
# 7️⃣ Generate Timetable
# -------------------------
generate = st.button("✨ Generate Study Planner", key="generate_btn")

if generate:
    if subjects == "" or len(days) == 0:
        st.warning("Please enter subjects and select study days")
    else:
        total_slots = sum(len(v) for v in day_time_slots.values())
        if total_slots == 0:
            st.warning("Please select study hours")
        else:
            # --- PRIORITY CALCULATION ---
            today = datetime.date.today()
            priority_scores = {}
            for subject in subject_list:
                days_left = (exam_dates[subject] - today).days
                urgency = 100 if days_left <= 0 else max(1, 100 - days_left)
                priority_scores[subject] = importance[subject] + urgency

            total_priority = sum(priority_scores.values())
            subject_pool = []
            for subject in subject_list:
                slots = round((priority_scores[subject] / total_priority) * total_slots)
                subject_pool += [subject] * slots
            while len(subject_pool) < total_slots:
                subject_pool.append(random.choice(subject_list))
            random.shuffle(subject_pool)

            # --- TIMETABLE (Markdown Table, Outline Only) ---
            st.header("Weekly Study Timetable")
            timetable_data = []

            # Table header
            table_md = "| Time | " + " | ".join(days) + " |\n"
            table_md += "|---" * (len(days) + 1) + "|\n"

            index = 0
            all_times = sorted(set(sum(day_time_slots.values(), [])))
            for time in all_times:
                row = f"| {time} "
                for day in days:
                    if time in day_time_slots[day]:
                        # Pomodoro breaks every 4 sessions
                        if study_mode == "Pomodoro (break every 4 sessions)" and index % 4 == 3:
                            subject = "Break"
                        else:
                            subject = subject_pool[index]
                        row += f"| {subject} "
                        timetable_data.append({"Day": day, "Time": time, "Subject": subject})
                        index += 1
                    else:
                        row += "|  "
                row += "|"
                table_md += row + "\n"

            st.markdown(table_md)
            st.success("✅ Study Planner Generated!")

            # --- EXPORT TO EXCEL ---
            df = pd.DataFrame(timetable_data)[["Day", "Time", "Subject"]]
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Timetable (Excel)",
                csv,
                "study_timetable.csv",
                "text/csv"
            )