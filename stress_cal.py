import streamlit as st

st.set_page_config(page_title="Student Stress Detector")

st.title("📊 Student Stress Level Detector")

st.write(
"This short questionnaire helps estimate your current **study stress level**. "
"Please answer the following 5 questions."
)

st.write("Rate each statement from **1 to 5**")

st.write("1 = Never")
st.write("2 = Rarely")
st.write("3 = Sometimes")
st.write("4 = Often")
st.write("5 = Always")

st.write("---")

# Questions
q1 = st.slider(
    "1️⃣ I feel overwhelmed by my academic workload.",
    1,5,3
)

q2 = st.slider(
    "2️⃣ I find it difficult to concentrate while studying.",
    1,5,3
)

q3 = st.slider(
    "3️⃣ I feel anxious about exams or deadlines.",
    1,5,3
)

q4 = st.slider(
    "4️⃣ I feel mentally tired after studying.",
    1,5,3
)

q5 = st.slider(
    "5️⃣ I feel I don't have enough time to complete my studies.",
    1,5,3
)

# Button
if st.button("Check My Stress Level"):

    total_score = q1 + q2 + q3 + q4 + q5

    st.write("Your stress score:", total_score)

    # Stress classification
    if total_score <= 10:
        level = "Low Stress"
        message = "You seem to be managing your studies well. Keep maintaining a balanced study routine."

    elif total_score <= 18:
        level = "Medium Stress"
        message = "You may be experiencing moderate study pressure. Try organizing your study time and taking regular breaks."

    else:
        level = "High Stress"
        message = "Your stress level appears high. It is important to take longer breaks, relax, and manage your study load carefully."

    st.subheader(f"Stress Level: {level}")

    st.write(message)

    st.write(
    "Tip: Regular breaks, proper sleep, and exercise can help reduce academic stress."
)