import streamlit as st
from questions import demo_questions, questions
import requests
from datetime import datetime

# --- Configure Yoco secret key ---
# Use sandbox key for local testing, live key when deployed publicly
YOCO_SECRET_KEY = "sk_test_yourSandboxKeyHere"

# --- Sidebar Branding ---
st.sidebar.image("logo.png", width="stretch")  # place logo.png in same folder
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

    This app is ideal for parents who want structured practice for their children, 
    and for learners who want to prepare for exams in a fun, interactive way.
    """
)

# --- Payment Gate ---
st.sidebar.title("Quiz Mode")

if "full_unlocked" not in st.session_state:
    st.session_state.full_unlocked = False

if st.sidebar.button("💳 Unlock Full Quiz (R100)", type="primary"):
    response = requests.post(
        "https://online.yoco.com/v1/checkouts",
        headers={"X-Auth-Secret-Key": YOCO_SECRET_KEY},
        json={
            "amount": 10000,   # cents = R100.00
            "currency": "ZAR",
            "successUrl": "http://localhost:8501?success=true",
            "cancelUrl": "http://localhost:8501?cancel=true"
        }
    )
    checkout = response.json()
    if "redirectUrl" in checkout:
        st.sidebar.markdown(f"[Click here to Pay R100]({checkout['redirectUrl']})")
    else:
        st.sidebar.error(f"Payment session could not be created: {checkout}")

# ✅ FIXED: use st.query_params
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

# Show question number clearly at the top
st.subheader(f"📊 Question {st.session_state.q_index + 1} of {len(active_questions)}")

# Radio button for answer selection
selected = st.radio(
    q["Question"],
    [q["OptionA"], q["OptionB"], q["OptionC"], q["OptionD"]],
    index=None,  # no default selection
    key=f"q{st.session_state.q_index}"
)

# Submit button checks correctness
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

# Navigation buttons
col1, col2, col3, col4 = st.columns(4)

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

with col4:
    if st.button("⬆️ Back to Top", type="secondary"):
        st.experimental_rerun()

# --- Certificate (optional future feature) ---
if st.session_state.full_unlocked and st.session_state.q_index == len(active_questions) - 1 and st.session_state.submitted:
    st.success("🎓 Congratulations! You completed the full quiz.")
    learner_name = st.text_input("Enter learner's name for certificate:")
    if st.button("📄 Download Certificate"):
        cert_text = f"Certificate of Achievement\n\nThis certifies that {learner_name} successfully completed the Maths8 Grade 8 Quiz on {datetime.today().strftime('%Y-%m-%d')}."
        st.download_button("Download Certificate", cert_text, file_name="certificate.txt")
