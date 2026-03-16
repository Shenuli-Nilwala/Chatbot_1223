import streamlit as st
import numpy as np
import random
from sklearn.ensemble import RandomForestRegressor
import shap

# -----------------------------
# Student Class
# -----------------------------
class Student:

    def __init__(self, name, subjects, priorities, stress_level, free_hours):
        self.name = name
        self.subjects = subjects
        self.priorities = priorities
        self.stress_level = stress_level
        self.free_hours = free_hours

        self.stress_map = {"Low":1, "Medium":2, "High":3}
        self.stress_num = self.stress_map[stress_level]


# -----------------------------
# AI Model Class
# -----------------------------
class AIModel:

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.explainer = None

    def train(self, priorities):

        X_train = []
        y_train = []

        for _ in range(600):
            for priority in priorities.values():

                stress_sim = random.randint(1,3)
                free_sim = random.randint(5,40)

                hours = (priority/5) * free_sim * (4 - stress_sim)/3

                X_train.append([stress_sim, priority, free_sim])
                y_train.append(hours)

        X_train = np.array(X_train)
        y_train = np.array(y_train)

        self.model.fit(X_train, y_train)

        self.explainer = shap.TreeExplainer(self.model)

    def predict(self, stress, priority, free_hours):

        pred = self.model.predict(
            np.array([[stress, priority, free_hours]])
        )[0]

        return pred

    def explain(self, stress, priority, free_hours):

        shap_values = self.explainer.shap_values(
            np.array([[stress, priority, free_hours]])
        )

        return shap_values[0]


# -----------------------------
# Study Advisor Class
# -----------------------------
class StudyAdvisor:

    def __init__(self, student, model):
        self.student = student
        self.model = model

    def calculate_hours(self):

        predictions = {}
        total = 0

        for subj in self.student.subjects:

            priority = self.student.priorities[subj]

            pred = self.model.predict(
                self.student.stress_num,
                priority,
                self.student.free_hours
            )

            predictions[subj] = pred
            total += pred

        scale = self.student.free_hours / total

        for subj in predictions:
            predictions[subj] = predictions[subj] * scale

        return predictions

    def break_recommendation(self):

        if self.student.stress_level == "High":

            break_time = 20
            reason = "Because your stress level is high, longer breaks help reduce mental fatigue."

        elif self.student.stress_level == "Medium":

            break_time = 15
            reason = "Your stress level is moderate, so medium breaks help maintain focus."

        else:

            break_time = 10
            reason = "Your stress level is low, so short breaks are enough to refresh your mind."

        return break_time, reason


# -----------------------------
# Streamlit App Class
# -----------------------------
class StudyApp:

    def run(self):

        st.set_page_config(page_title="AI Study Assistant", layout="wide")

        st.title("🤖 AI Study Assistant")

        st.write("Get personalized weekly study suggestions using AI.")

        st.sidebar.header("Student Information")

        name = st.sidebar.text_input("Enter your name")

        subjects_input = st.sidebar.text_input(
            "Enter subjects separated by commas",
            placeholder="Example: Math, Physics, Biology"
        )

        subjects = [s.strip() for s in subjects_input.split(",") if s.strip() != ""]

        priorities = {}

        for subj in subjects:
            priorities[subj] = st.sidebar.slider(
                f"Priority for {subj}",
                1,
                5,
                3
            )

        stress_level = st.sidebar.selectbox(
            "Stress level",
            ["Low","Medium","High"]
        )

        free_hours = st.sidebar.number_input(
            "Weekly free study hours",
            min_value=1,
            max_value=80,
            value=20
        )

        if st.sidebar.button("Generate Suggestions"):

            if not name or not subjects:
                st.warning("Please enter your name and subjects.")
                return

            student = Student(
                name,
                subjects,
                priorities,
                stress_level,
                free_hours
            )

            model = AIModel()
            model.train(priorities)

            advisor = StudyAdvisor(student, model)

            predictions = advisor.calculate_hours()

            break_time, break_reason = advisor.break_recommendation()

            st.header(f"Weekly Study Advice for {name}")

            for subj in subjects:

                hours_float = predictions[subj]

                hours = int(hours_float)
                minutes = int((hours_float - hours) * 60)

                shap_values = model.explain(
                    student.stress_num,
                    priorities[subj],
                    free_hours
                )

                stress_impact = round(shap_values[0],2)
                priority_impact = round(shap_values[1],2)
                free_impact = round(shap_values[2],2)

                st.subheader(subj)

                st.write(
                f"It is recommended to study **{subj}** for "
                f"**{hours} hours and {minutes} minutes** this week."
                )

                st.write(
                f"This is because this subject has priority level **{priorities[subj]}** "
                f"and you have **{free_hours} hours of free study time**."
                )

                st.write("AI Explanation:")

                st.write("Stress impact:", stress_impact)
                st.write("Priority impact:", priority_impact)
                st.write("Free time impact:", free_impact)

                st.write(
                f"Break recommendation: After 90 minutes of studying, take a "
                f"**{break_time} minute break**. {break_reason}"
                )

                st.write("---")


# -----------------------------
# Run App
# -----------------------------
app = StudyApp()
app.run()