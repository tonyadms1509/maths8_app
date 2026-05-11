import streamlit as st
from questions import demo_questions, questions
from datetime import datetime

# --- Sidebar Branding ---
st.sidebar.image("logo.png", width="stretch")
st.sidebar.markdown("🎓 Maths8 Quiz App — For Grade 8 learners")

# --- App Description ---
st.markdown(
    """
    # 📘 Maths8 Quiz App
    Welcome to the Maths8 Quiz App — designed for **Grade 8 learners**.  

    - 🎯 **Purpose:** Help learners build confidence in maths through practice.  
    - 📝 **Demo Mode:** Try 10 free sample questions to see how the app works.  
    - 💳 **Full Mode:** Parents can unlock 100 carefully prepared questions for R100.  
    - ✅ **Benefit:** Learners get instant feedback, explanations, and a certificate at the end.  
    """
)

# --- Payment Gate (Hosted Link) ---
st.sidebar.title("Quiz Mode")

if "full_unlocked" not in st.session_state:
    st.session_state.full_unlocked = False

if not st.session_state.full_unlocked:
    st.sidebar.markdown("💳 To unlock the full quiz, please pay R100:")
    # Replace with your actual Yoco hosted payment link
    st.sidebar.markdown("[Click here to Pay R100](https://pay.yoco.com/r/yourHostedLinkHere)")

# ✅ Detect success via query param
query_params = st.query_params
if "success" in query_params:
    st.session_state.full_unlocked = True

# --- Mode Selector ---
if st.session_state.full_unlocked:
    active_questions = questions
    st.sidebar.success("✅ Full Quiz Unlocked (100 questions)")
else:
    active_questions = demo_questions
    st.sidebar.info("Demo Mode: 10 free questions")

# --- Quiz Logic ---
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False

q = active_questions[st.session_state.q_index]

st.subheader(f"📊 Question {st.session_state.q_index + 1} of {len(active_questions)}")

selected = st.radio(
    q["Question"],
    [q["OptionA"], q["OptionB"], q["OptionC"], q["OptionD"]],
    index=None,
    key=f"q{st.session_state.q_index}"
)

if st.button("✅ Submit Answer", type="primary"):
    if selected is None:
        st.warning("⚠️ Please select an answer before submitting.")
    else:
        st.session_state.submitted = True
        if selected == q["Correct"]:
            st.success("🎉 Correct!")
        else:
            st.error(f"❌ Incorrect. The correct answer is {q['Correct']}.")
        st.info(q["Explanation"])

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Previous", type="secondary"):
        if st.session_state.q_index > 0:
            st.session_state.q_index -= 1
            st.session_state.submitted = False

with col2:
    if st.button("➡️ Next", type="secondary"):
        if st.session_state.submitted:
            if st.session_state.q_index < len(active_questions) - 1:
                st.session_state.q_index += 1
                st.session_state.submitted = False
        else:
            st.warning("⚠️ Please submit your answer before moving to the next question.")

with col3:
    if st.button("🔄 Restart Quiz", type="secondary"):
        st.session_state.q_index = 0
        st.session_state.submitted = False
        st.session_state.full_unlocked = False

# --- Certificate (Full Mode only) ---
if st.session_state.full_unlocked and st.session_state.q_index == len(active_questions) - 1 and st.session_state.submitted:
    st.success("🎓 Congratulations! You completed the full quiz.")
    learner_name = st.text_input("Enter learner's name for certificate:")
    if st.button("📄 Download Certificate"):
        cert_text = f"Certificate of Achievement\n\nThis certifies that {learner_name} successfully completed the Maths8 Grade 8 Quiz on {datetime.today().strftime('%Y-%m-%d')}."
        st.download_button("Download Certificate", cert_text, file_name="certificate.txt")
s