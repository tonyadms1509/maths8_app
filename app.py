import streamlit as st
from questions import demo_questions, questions
from datetime import datetime
import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# --- File to store paid users ---
PAID_USERS_FILE = "paid_users.csv"

def load_paid_users():
    if os.path.exists(PAID_USERS_FILE):
        return pd.read_csv(PAID_USERS_FILE)
    else:
        return pd.DataFrame(columns=["name", "email"])

def save_paid_user(name, email):
    users = load_paid_users()
    if email not in users["email"].values:
        users = pd.concat([users, pd.DataFrame([[name, email]], columns=["name", "email"])])
        users.to_csv(PAID_USERS_FILE, index=False)

# --- Branding ---
logo_path = "logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_column_width=True)
else:
    st.sidebar.warning("⚠️ Logo file not found. Please place logo.png in the app folder.")

st.sidebar.markdown("🎓 Maths Grade 8 Quiz App")

# --- Splash Screen ---
splash_path = "splash.png"
if os.path.exists(splash_path):
    st.image(splash_path, use_column_width=True)
else:
    st.info("Welcome to Maths Grade 8 Quiz — helping learners build confidence one question at a time!")

# --- Parent Registration ---
st.sidebar.title("Parent Registration")
parent_name = st.sidebar.text_input("Parent Name")
parent_email = st.sidebar.text_input("Parent Email")

users = load_paid_users()
if parent_email in users["email"].values:
    st.sidebar.success("✅ Payment already recorded. Full quiz unlocked.")
    st.session_state.full_unlocked = True
else:
    if "full_unlocked" not in st.session_state:
        st.session_state.full_unlocked = False

    if not st.session_state.full_unlocked:
        st.sidebar.markdown("💳 To unlock the full quiz, please pay R100:")
        st.sidebar.markdown("[Pay with Yoco](https://pay.yoco.com/r/mEJyod?redirectOnPaymentSuccess=https://maths8-app.streamlit.app)")

        st.sidebar.markdown("[Pay with PayPal](https://www.paypal.com/ncp/payment/GUBA8XCC45UYA)")
        st.sidebar.info(
            "Parents: After clicking a payment link, Yoco or PayPal will open in a new page. "
            "Please complete the payment securely. Once successful, you’ll be redirected "
            "back to this app automatically and the full 100‑question quiz will unlock."
        )

    # ✅ Detect success via query param
    query_params = st.query_params
    if "success" in query_params and parent_name and parent_email:
        st.session_state.full_unlocked = True
        save_paid_user(parent_name, parent_email)
        st.success("💳 Thank you for your payment! The full Maths Grade 8 quiz is now unlocked.")
        st.info("Parents: Your support helps learners build confidence in maths. Enjoy the full 100‑question experience!")

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
        if "thank_you_shown" in st.session_state:
            del st.session_state["thank_you_shown"]

# --- Certificate Generation ---
def generate_certificate(learner_name):
    cert_bg = Image.open("certificate.png")
    draw = ImageDraw.Draw(cert_bg)
    font = ImageFont.truetype("arial.ttf", 40)

    draw.text((400, 300), learner_name, font=font, fill="black")
    date_text = datetime.today().strftime("%Y-%m-%d")
    draw.text((400, 400), f"Date: {date_text}", font=font, fill="black")
    draw.text((400, 500), "Signed by StockLinkSA", font=font, fill="black")

    cert_bg.save("certificate_output.png")
    return "certificate_output.png"

if st.session_state.full_unlocked and st.session_state.q_index == len(active_questions) - 1 and st.session_state.submitted:
    st.success("🎓 Congratulations! You completed the full quiz.")
    learner_name = st.text_input("Enter learner's name for certificate:")
    if st.button("📄 Download Certificate"):
        cert_file = generate_certificate(learner_name)
        with open(cert_file, "rb") as f:
            st.download_button("Download Certificate", f, file_name="certificate.png")

# --- Footer ---
st.markdown("---")
st.markdown("🔗 Powered by **StockLinkSA · Maths Grade 8 Quiz**")
