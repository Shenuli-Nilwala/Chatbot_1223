import streamlit as st
import pandas as pd
import os
import altair as alt

# --- Page Setup ---
st.set_page_config(page_title="Student Burnout Dashboard", layout="wide")
st.title("Student Burnout & Engagement Monitoring System")

# --- File paths ---
user_file = "user_info.csv"
log_file = "daily_logs.csv"

# --- Sidebar: One-Time User Info ---
st.sidebar.header("👤 Setup / One-Time Info")

# If user info file does not exist or is empty, ask user to enter info
if not os.path.exists(user_file) or os.path.getsize(user_file) == 0:
    name = st.sidebar.text_input("Enter your name:")

    # User enters subjects freely; show example in placeholder
    subjects_input = st.sidebar.text_input(
        "Enter your subjects (separate by commas):", 
        placeholder="Example: Math, Physics, Biology"
    )
    subjects = [s.strip() for s in subjects_input.split(",") if s.strip() != ""]  # clean list

    target_hours = st.sidebar.slider("Target study hours per day:", 1, 10, 4)

    if st.sidebar.button("Save Info"):
        # Save user info to CSV
        user_df = pd.DataFrame({
            "Name": [name],
            "Subjects": [",".join(subjects)],
            "Target_Hours": [target_hours]
        })
        user_df.to_csv(user_file, index=False)
        st.sidebar.success("User info saved!")

# --- Load user info safely ---
if os.path.exists(user_file) and os.path.getsize(user_file) > 0:
    user_df = pd.read_csv(user_file)
    st.sidebar.write("Current User Info:")
    st.sidebar.write(user_df)
else:
    user_df = pd.DataFrame()  # empty dataframe if file doesn't exist or is empty

# --- Daily Study Log Form ---
st.header("📝 Daily Study Log")
with st.form("daily_log_form"):
    task = st.text_input("Task / Topic studied today:")
    study_hours = st.slider("Hours spent today:", 0.5, 10.0, 2.0)
    stress_level = st.selectbox("How stressed or tired are you?", ["Low", "Medium", "High"])
    breaks_taken = st.number_input("Number of breaks taken:", 0, 10)
    submitted = st.form_submit_button("Submit Log")

    if submitted:
        # Create a new log entry
        new_log = pd.DataFrame({
            "Task": [task],
            "Study_Hours": [study_hours],
            "Stress": [stress_level],
            "Breaks": [breaks_taken],
            "Date": [pd.Timestamp.now().date()]
        })

        # Append to existing logs or create new CSV
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            daily_logs = pd.read_csv(log_file)
            daily_logs = pd.concat([daily_logs, new_log], ignore_index=True)
        else:
            daily_logs = new_log

        daily_logs.to_csv(log_file, index=False)
        st.success("Daily log saved!")

# --- Load daily logs safely ---
if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
    daily_logs = pd.read_csv(log_file)

    # --- Study Hours Chart ---
    st.subheader("📊 Study Hours Over Time")
    df_hours = daily_logs.groupby("Date")["Study_Hours"].sum().reset_index()
    chart_hours = alt.Chart(df_hours).mark_line(point=True).encode(
        x="Date",
        y="Study_Hours"
    )
    st.altair_chart(chart_hours, use_container_width=True)

    # --- Stress Level Chart ---
    st.subheader("😓 Stress Level Over Time")
    stress_map = {"Low": 1, "Medium": 2, "High": 3}
    daily_logs["Stress_Num"] = daily_logs["Stress"].map(stress_map)
    df_stress = daily_logs.groupby("Date")["Stress_Num"].mean().reset_index()
    chart_stress = alt.Chart(df_stress).mark_line(point=True).encode(
        x="Date",
        y="Stress_Num",
        color=alt.Color("Stress_Num", scale=alt.Scale(domain=[1,3], range=["green","orange","red"]))
    )
    st.altair_chart(chart_stress, use_container_width=True)

    # --- Task Completion Pie Chart ---
    st.subheader("✅ Task Completion Overview")
    task_count = daily_logs["Task"].value_counts().reset_index()
    task_count.columns = ["Task", "Count"]
    st.altair_chart(
        alt.Chart(task_count).mark_arc().encode(
            theta="Count",
            color="Task",
            tooltip=["Task","Count"]
        ),
        use_container_width=True
    )

    # --- Burnout Risk Assessment ---
    st.subheader("🔥 Burnout Risk Assessment")
    avg_stress = daily_logs["Stress_Num"].mean()
    total_hours = daily_logs["Study_Hours"].sum()
    target_hours = user_df["Target_Hours"].iloc[0] if not user_df.empty else 4

    if avg_stress >= 2.5 or total_hours > target_hours * len(daily_logs):
        burnout_risk = "High"
    elif avg_stress >= 1.5:
        burnout_risk = "Medium"
    else:
        burnout_risk = "Low"
    st.metric("Current Burnout Risk", burnout_risk)