import streamlit as st
from questions import demo_questions, questions
import requests
from datetime import datetime

# --- Configure Yoco secret key ---
# Use sandbox key for testing, live key when deployed
YOCO_SECRET_KEY = "sk_test_yourSandboxKeyHere"

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

# --- Payment Gate ---
st.sidebar.title("Quiz Mode")

if "full_unlocked" not in st.session_state:
    st.session_state.full_unlocked = False

if st.sidebar.button("💳 Unlock Full Quiz (R100)", type="primary"):
    try:
        response = requests.post(
            "https://online.yoco.com/v1/checkouts",
            headers={
                "X-Auth-Secret-Key": YOCO_SECRET_KEY,
                "Content-Type": "application/json"
            },
            json={
                "amount": 10000,   # cents = R100.00
                "currency": "ZAR",
                "successUrl": "https://maths8-app.streamlit.app?success=true",
                "cancelUrl": "https://maths8-app.streamlit.app?cancel=true"
            }
        )
        if response.status_code == 200:
            checkout = response.json()
            if "redirectUrl" in checkout:
                st.sidebar.markdown(f"[Click here to Pay R100]({checkout['redirectUrl']})")
            else:
                st.sidebar.error("⚠️ Payment session created but no redirect URL.")
        else:
            st.sidebar.error(f"⚠️ Payment request failed: {response.status_code}")
            st.sidebar.text(response.text)  # show raw error for debugging
    except Exception as e:
        st.sidebar.error(f"⚠️ Error creating payment session: {e}")

# ✅ Detect success
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
