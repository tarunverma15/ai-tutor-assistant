import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from reader import extract_text
from generator import QuestionGenerator
from evaluator import Evaluator
from explanation import Explanation
from performance import PerformanceAnalyzer

load_dotenv()

API_KEY = os.getenv("GROQ_APIKEY")

client = Groq(api_key=API_KEY)

MODEL = "llama-3.3-70b-versatile"

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide"
)

# =========================================================
# GLOBAL STYLES
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

.main{
    padding-top:0px;
}

.block-container{
    padding-top:2rem;
    padding-bottom:3rem;
    max-width: 1100px;
}

/* Hero header */
.hero{
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    padding: 32px 40px;
    border-radius: 18px;
    margin-bottom: 28px;
    box-shadow: 0 10px 30px rgba(79,70,229,0.25);
}
.hero h1{
    color:#ffffff;
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 4px;
}
.hero p{
    color: rgba(255,255,255,0.9);
    font-size: 16px;
    margin: 0;
}

/* Cards */
.card{
    background: #ffffff;
    border: 1px solid #EEF0F6;
    border-radius: 16px;
    padding: 24px 28px;
    box-shadow: 0 2px 10px rgba(17,17,17,0.04);
    margin-bottom: 18px;
}

/* Badges */
.badge{
    display:inline-block;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    margin-right: 8px;
}
.badge-purple{ background:#EEF0FF; color:#4F46E5; }
.badge-green{ background:#E7F9EE; color:#15803D; }
.badge-amber{ background:#FFF6E5; color:#B45309; }
.badge-red{ background:#FDEDEE; color:#B91C1C; }

/* Question header */
.q-index{
    color:#6B7280;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}
.q-text{
    font-size: 20px;
    font-weight: 700;
    color:#111827;
    margin-top: 4px;
    margin-bottom: 18px;
}

h1{ color:#4F46E5; }

.stButton>button{
    width:100%;
    border-radius:10px;
    height:48px;
    font-size:16px;
    font-weight:600;
    border: none;
}

.stButton>button:hover{
    opacity: 0.92;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background: #F9FAFB;
    border-right: 1px solid #EEF0F6;
}
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] .stMarkdown h1{
    font-size: 20px;
    color: #111827;
}

/* Divider spacing tighter */
hr{ margin: 1.2rem 0; }

/* Feedback panel */
.feedback-box{
    background:#F9FAFB;
    border-left: 4px solid #4F46E5;
    border-radius: 10px;
    padding: 18px 22px;
    margin-top: 10px;
}

footer, #MainMenu {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HERO HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <h1>🎓 AI Study Assistant</h1>
    <p>Turn any PDF, DOCX, or image into a personalized, AI-graded quiz.</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("## ⚙️ Quiz Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    [
        "Easy",
        "Medium",
        "Hard"
    ]
)

question_type = st.sidebar.selectbox(
    "Question Type",
    [
        "MCQ",
        "Short Answer",
        "Long Answer",
        "True/False",
        "Fill in the Blanks",
        "One Word"
    ]
)

num_questions = st.sidebar.slider(
    "Number of Questions",
    1,
    20,
    5
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 📁 Study Material")

uploaded_file = st.sidebar.file_uploader(
    "Upload a file",
    type=[
        "pdf",
        "docx",
        "png",
        "jpg",
        "jpeg",
        "bmp",
        "tiff"
    ],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    st.sidebar.caption(f"📄 {uploaded_file.name}")

generate_clicked = st.sidebar.button("🚀 Generate Quiz")

# =========================================================
# SESSION STATE INIT
# =========================================================

if "quiz_started" not in st.session_state:
    st.session_state.quiz_started=False

if "knowledge" not in st.session_state:
    st.session_state.knowledge=""

if "questions" not in st.session_state:
    st.session_state.questions=[]

if "current_question" not in st.session_state:
    st.session_state.current_question=0

if "previous_questions" not in st.session_state:
    st.session_state.previous_questions=[]

if "performance" not in st.session_state:
    st.session_state.performance=PerformanceAnalyzer()

if "score" not in st.session_state:
    st.session_state.score=0

if "show_result" not in st.session_state:
    st.session_state.show_result=False

if "user_answer" not in st.session_state:
    st.session_state.user_answer=""

if "quiz_finished" not in st.session_state:
    st.session_state.quiz_finished=False

generator = QuestionGenerator(
    client,
    MODEL
)

evaluator = Evaluator(
    client,
    MODEL
)

teacher = Explanation(
    client,
    MODEL
)

# Badge helper for difficulty
DIFFICULTY_BADGE = {
    "Easy": "badge-green",
    "Medium": "badge-amber",
    "Hard": "badge-red",
}

if generate_clicked:

    if uploaded_file is None:
        st.error("Please upload a file.")
        st.stop()

    os.makedirs("temp",exist_ok=True)

    filepath=Path("temp")/uploaded_file.name

    with open(filepath,"wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Extracting text..."):

        knowledge=extract_text(filepath)

    st.session_state.knowledge=knowledge

    st.session_state.quiz_started=True

    st.success("✅ Knowledge extracted successfully.")

# -----------------------------
# Generate Questions
# -----------------------------

if st.session_state.quiz_started and len(st.session_state.questions) == 0:

    with st.spinner("Generating Questions..."):

        for _ in range(num_questions):

            quiz = generator.generate_question(
                st.session_state.knowledge,
                difficulty,
                question_type,
                st.session_state.previous_questions
            )

            st.session_state.questions.append(quiz)

            st.session_state.previous_questions.append(
                quiz["question"]
            )

    st.success("🎉 Quiz Generated Successfully!")

if st.session_state.quiz_started and len(st.session_state.questions) > 0:

    current = st.session_state.current_question

    total = len(st.session_state.questions)

    quiz = st.session_state.questions[current]

    # ---- Progress bar ----
    st.progress((current) / total if total else 0)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    diff_badge_class = DIFFICULTY_BADGE.get(difficulty, "badge-purple")

    badges_html = f"""
    <span class="badge {diff_badge_class}">{difficulty}</span>
    <span class="badge badge-purple">{quiz.get("question_type","")}</span>
    """

    if "topic" in quiz:
        badges_html += f'<span class="badge badge-purple">📚 {quiz["topic"]}</span>'

    st.markdown(badges_html, unsafe_allow_html=True)

    st.markdown(f'<div class="q-index">Question {current+1} of {total}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="q-text">{quiz["question"]}</div>', unsafe_allow_html=True)

    qtype = quiz["question_type"]

    if qtype == "MCQ":

        answer = st.radio(

            "Choose Answer",

            quiz["options"],

            key=f"answer_{current}"

        )

    elif qtype == "True/False":

        answer = st.radio(

            "Choose",

            [

                "True",

                "False"

            ],

            key=f"answer_{current}"

        )

    elif qtype == "Fill in the Blanks":

        answer = st.text_input(

            "Answer",

            key=f"answer_{current}"

        )

    elif qtype == "One Word":

        answer = st.text_input(

            "Answer",

            key=f"answer_{current}"

        )

    else:

        answer = st.text_area(

            "Write your answer",

            height=250,

            key=f"answer_{current}"

        )

    col1,col2 = st.columns(2)

    with col1:

        if current>0:

            if st.button("⬅ Previous"):

                st.session_state.current_question-=1

                st.rerun()

    with col2:

        if st.button("✅ Submit Answer"):

            st.session_state.user_answer = answer

            st.session_state.show_result = True

            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Show Result
# -----------------------------

    if st.session_state.show_result:

        with st.spinner("Evaluating your answer..."):

            result = evaluator.evaluate(
                quiz,
                st.session_state.user_answer
            )

        st.session_state.performance.update(
            quiz,
            result,
            difficulty
        )

        st.markdown('<div class="card">', unsafe_allow_html=True)

        if result.get("correct") is True:

            st.success("✅ Correct")

            st.session_state.score += result["marks"]

        elif result.get("correct") is False:

            st.error("❌ Wrong")

        else:

            st.info(
                f"Marks : {result['marks']} / {result['max_marks']}"
            )

            st.session_state.score += result["marks"]

        st.markdown("#### 💬 Feedback")
        st.markdown(f'<div class="feedback-box">{result["feedback"]}</div>', unsafe_allow_html=True)

        if "missing_points" in result:

            st.warning("**Missing Points**")
            st.write(result["missing_points"])

        if "ideal_answer" in result:

            st.success("**Ideal Answer**")
            st.write(result["ideal_answer"])

        with st.spinner("Generating Explanation..."):

            explanation = teacher.explain(quiz)

        st.markdown("#### 📖 Explanation")
        st.markdown(f'<div class="feedback-box">{explanation}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Current Score",
                st.session_state.score
            )

        with c2:

            st.metric(
                "Question",
                f"{current+1}/{total}"
            )

        # -------------------------
        # NEXT BUTTON
        # -------------------------

        if current < total-1:

            if st.button("➡ Next Question"):

                st.session_state.current_question += 1

                st.session_state.show_result = False

                st.session_state.user_answer = ""

                st.rerun()

        else:

            st.success("🎉 Quiz Completed!")

            st.balloons()

            st.session_state.quiz_finished = True

# ===========================================
# FINAL DASHBOARD
# ===========================================

if st.session_state.get("quiz_finished", False):

    st.markdown("## 📊 Performance Dashboard")

    performance = st.session_state.performance

    total = performance.total_questions
    correct = performance.correct
    wrong = performance.wrong

    accuracy = (correct / total * 100) if total else 0

    if accuracy >= 90:
        grade = "A+"
    elif accuracy >= 80:
        grade = "A"
    elif accuracy >= 70:
        grade = "B"
    elif accuracy >= 60:
        grade = "C"
    else:
        grade = "Needs Improvement"

    st.markdown('<div class="card">', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Questions", total)
    c2.metric("Correct", correct)
    c3.metric("Wrong", wrong)
    c4.metric("Accuracy", f"{accuracy:.1f}%")

    st.progress(accuracy / 100)

    st.success(f"🏆 Grade : {grade}")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📚 Topic-wise Performance")

    topic_data = {}

    for topic, stat in performance.topic_stats.items():

        total_topic = stat["correct"] + stat["wrong"]

        if total_topic:
            topic_data[topic] = (
                stat["correct"] / total_topic
            ) * 100

    if topic_data:
        st.bar_chart(topic_data)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎯 Difficulty-wise Performance")

    diff_data = {}

    for diff, stat in performance.difficulty_stats.items():

        total_diff = stat["correct"] + stat["wrong"]

        if total_diff:
            diff_data[diff] = (
                stat["correct"] / total_diff
            ) * 100

    if diff_data:
        st.bar_chart(diff_data)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Question Type Performance")

    type_data = {}

    for qtype, stat in performance.question_type_stats.items():

        total_type = stat["correct"] + stat["wrong"]

        if total_type:
            type_data[qtype] = (
                stat["correct"] / total_type
            ) * 100

    if type_data:
        st.bar_chart(type_data)
    st.markdown('</div>', unsafe_allow_html=True)

    report = f"""
AI STUDY ASSISTANT REPORT

Total Questions : {total}

Correct : {correct}

Wrong : {wrong}

Accuracy : {accuracy:.2f}%

Grade : {grade}

"""

    col_dl, col_new = st.columns(2)

    with col_dl:
        st.download_button(
            "⬇ Download Report",
            report,
            file_name="Performance_Report.txt"
        )

    with col_new:
        if st.button("🔄 Start New Quiz"):

            st.session_state.quiz_started = False
            st.session_state.quiz_finished = False
            st.session_state.questions = []
            st.session_state.previous_questions = []
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.user_answer = ""
            st.session_state.show_result = False
            st.session_state.knowledge = ""
            st.session_state.performance = PerformanceAnalyzer()

            st.rerun()

# =========================================================
# EMPTY STATE (nothing uploaded / started yet)
# =========================================================

if not st.session_state.quiz_started:

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
### 👋 Get Started

1. Upload a PDF, DOCX, or image from the sidebar.
2. Choose your difficulty, question type, and number of questions.
3. Click **🚀 Generate Quiz** and start learning!
""")
    st.markdown('</div>', unsafe_allow_html=True)
