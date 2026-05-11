import streamlit as st
from questions import demo_questions

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
    - ✅ **Benefit:** Learners get instant feedback and explanations.  
    """
)

# --- Quiz Logic ---
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False

active_questions = demo_questions
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
