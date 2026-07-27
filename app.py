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

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

load_dotenv()

api_key = "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"
client = Groq(api_key=api_key) if api_key else None


MODEL = "llama3-70b-8192" 


generator = QuestionGenerator(client, MODEL)
evaluator = Evaluator(client, MODEL)
explainer = Explanation(client, MODEL)

# =========================================================
# THEME CONFIGURATION
# =========================================================

if "theme" not in st.session_state:
    st.session_state.theme = "light"

THEMES = {
    "light": {
        "bg": "#F5F3EF",
        "surface": "#FFFFFF",
        "surface_2": "#F8FAF9",
        "card_border": "#0E2A38",
        "border_soft": "#E2E8F0",
        "text": "#0F172A",
        "text_muted": "rgba(15, 23, 42, 0.65)",
        "accent": "#0284C7",
        "accent_dark": "#0369A1",
        "accent_soft": "rgba(2, 132, 199, 0.10)",
        "dot_color": "#0284C7",
        "btn_bg": "linear-gradient(135deg, #0284C7 0%, #2563EB 100%)",
        "btn_text": "#FFFFFF",
        "input_bg": "#FFFFFF",
        "input_text": "#0F172A",
        "shadow": "0 20px 40px -12px rgba(15, 23, 42, 0.08), 0 0 0 1px rgba(14, 42, 56, 0.12)",
        "cloud_stroke": "#0E2A38",
        "cloud_accent": "#0284C7",
        "cloud_bg": "rgba(2, 132, 199, 0.08)",
        "popover_bg": "#FFFFFF",
        "popover_text": "#0F172A",
    },
    "dark": {
        "bg": "#0B1317",
        "surface": "#121E24",
        "surface_2": "#172730",
        "card_border": "#2DD4BF",
        "border_soft": "rgba(45, 212, 191, 0.25)",
        "text": "#FFFFFF",
        "text_muted": "rgba(255, 255, 255, 0.70)",
        "accent": "#2DD4BF",
        "accent_dark": "#14B8A6",
        "accent_soft": "rgba(45, 212, 191, 0.15)",
        "dot_color": "#2DD4BF",
        "btn_bg": "linear-gradient(135deg, #2DD4BF 0%, #0EA5E9 100%)",
        "btn_text": "#0B1317",
        "input_bg": "#172730",
        "input_text": "#FFFFFF",
        "shadow": "0 0 25px rgba(45, 212, 191, 0.18), 0 0 0 1px rgba(45, 212, 191, 0.35)",
        "cloud_stroke": "#2DD4BF",
        "cloud_accent": "#38BDF8",
        "cloud_bg": "rgba(45, 212, 191, 0.12)",
        "popover_bg": "#172730",
        "popover_text": "#FFFFFF",
    },
}

T = THEMES[st.session_state.theme]

# =========================================================
# GLOBAL CSS OVERRIDES
# =========================================================

css_style = f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {{
--bg: {T['bg']};
--surface: {T['surface']};
--surface-2: {T['surface_2']};
--card-border: {T['card_border']};
--border-soft: {T['border_soft']};
--text: {T['text']};
--text-muted: {T['text_muted']};
--accent: {T['accent']};
--accent-dark: {T['accent_dark']};
--accent-soft: {T['accent_soft']};
--dot-color: {T['dot_color']};
--btn-bg: {T['btn_bg']};
--btn-text: {T['btn_text']};
--input-bg: {T['input_bg']};
--input-text: {T['input_text']};
--shadow: {T['shadow']};
--cloud-stroke: {T['cloud_stroke']};
--cloud-accent: {T['cloud_accent']};
--cloud-bg: {T['cloud_bg']};
--popover-bg: {T['popover_bg']};
--popover-text: {T['popover_text']};
}}

html, body, [class*="css"] {{
font-family: 'Inter', 'Plus Jakarta Sans', sans-serif;
color: var(--text);
}}

body, .stApp {{
background-color: var(--bg) !important;
}}

header[data-testid="stHeader"] {{
background: transparent !important;
border: none !important;
}}

.block-container {{
padding-top: 1.5rem !important;
padding-bottom: 3.5rem !important;
padding-left: 2rem !important;
padding-right: 2rem !important;
max-width: 1150px !important;
margin: 0 auto !important;
}}

[data-testid="stColumn"], 
[data-testid="stHorizontalBlock"], 
[data-testid="stVerticalBlock"], 
[data-testid="stElementContainer"],
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
border: none !important;
box-shadow: none !important;
outline: none !important;
background: transparent !important;
}}

h1, h2, h3, h4 {{
color: var(--text) !important;
font-family: 'Playfair Display', serif !important;
font-weight: 700;
}}

p, span, label, div {{
font-family: 'Inter', sans-serif;
}}

.top-nav-bar {{
display: flex;
justify-content: space-between;
align-items: center;
margin-bottom: 20px;
}}
.brand-badge {{
display: inline-flex;
align-items: center;
gap: 8px;
font-weight: 800;
font-size: 15px;
letter-spacing: -0.01em;
color: var(--text);
}}
.brand-mark {{
width: 28px;
height: 28px;
border-radius: 8px;
background: var(--btn-bg);
color: #FFFFFF;
display: inline-flex;
align-items: center;
justify-content: center;
font-family: 'Playfair Display', serif;
font-weight: 800;
font-size: 15px;
}}

.theme-toggle-btn button {{
background: var(--surface) !important;
border: 1.8px solid var(--card-border) !important;
color: var(--text) !important;
border-radius: 9999px !important;
padding: 6px 18px !important;
font-size: 13px !important;
font-weight: 700 !important;
box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
.theme-toggle-btn button:hover {{
transform: translateY(-2px) !important;
border-color: var(--accent) !important;
color: var(--accent) !important;
}}

.hero-wrapper {{
text-align: center;
margin-bottom: 36px;
}}
.hero-wrapper h1 {{
font-size: 48px !important;
font-weight: 800 !important;
letter-spacing: -0.02em;
margin-bottom: 8px !important;
color: var(--text) !important;
}}
.hero-wrapper p {{
color: var(--text-muted) !important;
font-size: 16px !important;
font-weight: 500;
margin: 0 !important;
}}

.saas-card-box {{
background: var(--surface);
border: 1.8px solid var(--card-border);
border-radius: 24px;
padding: 28px 30px;
box-shadow: var(--shadow);
height: 100%;
box-sizing: border-box;
transition: transform 0.25s ease, box-shadow 0.25s ease;
position: relative;
overflow: hidden;
}}
.saas-card-box::before {{
content: '';
position: absolute;
top: 0;
left: 0;
right: 0;
height: 4px;
background: var(--btn-bg);
}}

.card-title-row {{
display: flex;
align-items: center;
gap: 12px;
margin-bottom: 4px;
}}
.card-title-row .dot-indicator {{
width: 12px;
height: 12px;
border-radius: 50%;
background-color: var(--dot-color);
display: inline-block;
flex-shrink: 0;
box-shadow: 0 0 10px var(--accent);
}}
.card-title-row h2 {{
font-family: 'Playfair Display', serif !important;
font-size: 24px !important;
font-weight: 800 !important;
color: var(--text) !important;
margin: 0 !important;
}}
.card-desc {{
font-size: 13.5px;
color: var(--text-muted);
margin-left: 24px;
margin-bottom: 18px;
font-weight: 500;
}}

@keyframes floatGraphic {{
0% {{ transform: translateY(0px); }}
50% {{ transform: translateY(-7px); }}
100% {{ transform: translateY(0px); }}
}}
.cloud-graphic-box {{
display: flex;
justify-content: center;
align-items: center;
margin-bottom: 16px;
animation: floatGraphic 4s ease-in-out infinite;
}}

[data-testid="stFileUploaderDropzone"] {{
background: var(--surface-2) !important;
border: 1.8px dashed var(--card-border) !important;
border-radius: 18px !important;
padding: 20px 16px !important;
margin-top: 6px !important;
transition: all 0.25s ease !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
border-color: var(--accent) !important;
background: var(--accent-soft) !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] {{
color: var(--text) !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzoneInstructions"] div {{
color: var(--text) !important;
font-weight: 600 !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] svg {{
fill: var(--cloud-accent) !important;
}}
[data-testid="stFileUploaderDropzone"] button {{
background: var(--btn-bg) !important;
color: var(--btn-text) !important;
border: none !important;
border-radius: 9999px !important;
font-weight: 800 !important;
padding: 8px 22px !important;
box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12) !important;
transition: transform 0.2s ease !important;
}}
[data-testid="stFileUploaderDropzone"] button:hover {{
transform: translateY(-2px) !important;
}}

.config-group-card {{
background: var(--surface-2);
border: 1.8px solid var(--card-border);
border-radius: 18px;
padding: 16px 20px;
margin-bottom: 16px;
}}
.config-group-header {{
display: flex;
align-items: center;
gap: 10px;
margin-bottom: 8px;
}}
.config-group-header .icon {{
font-size: 18px;
color: var(--accent);
}}
.config-group-header .title {{
font-size: 15px;
font-weight: 800;
color: var(--text);
}}

div[data-baseweb="select"] > div {{
background: var(--surface) !important;
border: 1.8px solid var(--card-border) !important;
border-radius: 12px !important;
color: var(--input-text) !important;
font-weight: 700 !important;
font-size: 14.5px !important;
}}
div[data-baseweb="select"] *:not(svg) {{
color: var(--input-text) !important;
}}
div[data-baseweb="select"] svg {{
fill: var(--input-text) !important;
}}

div[data-baseweb="popover"] {{
background: transparent !important;
}}
div[data-baseweb="popover"] ul[data-baseweb="menu"] {{
background-color: var(--popover-bg) !important;
border: 1.8px solid var(--card-border) !important;
border-radius: 14px !important;
box-shadow: 0 12px 36px rgba(0, 0, 0, 0.20) !important;
padding: 6px !important;
}}
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] [role="option"],
div[data-baseweb="popover"] li * {{
background-color: transparent !important;
color: var(--popover-text) !important;
font-size: 14px !important;
font-weight: 700 !important;
border-radius: 8px !important;
}}
div[data-baseweb="popover"] li:hover,
div[data-baseweb="popover"] [role="option"]:hover,
div[data-baseweb="popover"] li[aria-selected="true"] {{
background-color: var(--accent-soft) !important;
color: var(--accent) !important;
}}

.slider-container-card {{
background: var(--surface-2);
border: 1.8px solid var(--card-border);
border-radius: 18px;
padding: 16px 20px 12px 20px;
}}
.slider-lbl {{
font-size: 15px;
font-weight: 800;
color: var(--text);
margin-bottom: 8px;
}}
[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child {{
background: var(--border-soft) !important;
height: 7px !important;
border-radius: 9999px !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] > div > div:first-child {{
background: var(--accent) !important;
height: 7px !important;
border-radius: 9999px !important;
}}
[data-testid="stSlider"] div[role="slider"] {{
background: var(--accent) !important;
border: 2.5px solid #FFFFFF !important;
box-shadow: 0 0 0 4px var(--accent-soft) !important;
width: 20px !important;
height: 20px !important;
}}
.slider-meta-row {{
display: flex;
justify-content: space-between;
align-items: center;
font-size: 12.5px;
font-weight: 800;
color: var(--text-muted);
margin-top: 4px;
}}
.slider-meta-val {{
color: var(--accent);
font-weight: 800;
background: var(--accent-soft);
padding: 2px 10px;
border-radius: 9999px;
}}

div[data-testid="stButton"] button {{
border-radius: 9999px !important;
height: 52px !important;
font-size: 16px !important;
font-weight: 800 !important;
border: 1.8px solid var(--card-border) !important;
background: var(--surface) !important;
color: var(--text) !important;
box-shadow: var(--shadow) !important;
transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
div[data-testid="stButton"] button:hover {{
transform: translateY(-2px) !important;
border-color: var(--accent) !important;
color: var(--accent) !important;
}}
div[data-testid="stButton"] button[kind="primary"] {{
background: var(--btn-bg) !important;
color: var(--btn-text) !important;
border: none !important;
box-shadow: 0 8px 24px rgba(2, 132, 199, 0.3) !important;
}}
div[data-testid="stButton"] button[kind="primary"]:hover {{
transform: translateY(-2px) !important;
box-shadow: 0 12px 28px rgba(2, 132, 199, 0.45) !important;
color: var(--btn-text) !important;
}}

footer, #MainMenu {{ visibility: hidden; }}
</style>"""

st.markdown(css_style, unsafe_allow_html=True)

# =========================================================
# TOP NAVIGATION BAR
# =========================================================

nav_html = """<div class="top-nav-bar"><div class="brand-badge"><span class="brand-mark">A</span> AI Study Assistant</div></div>"""
st.markdown(nav_html, unsafe_allow_html=True)

col_n1, col_n2 = st.columns([9, 1.5])
with col_n2:
    st.markdown('<div class="theme-toggle-btn">', unsafe_allow_html=True)
    theme_text = "Light Mode" if st.session_state.theme == "dark" else "Dark Mode"
    if st.button(theme_text, key="theme_toggle_btn"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# HERO SECTION
# =========================================================

hero_html = """<div class="hero-wrapper"><h1>AI Study Assistant</h1><p>Turn any PDF, DOCX, or image into a personalized, AI-graded quiz.</p></div>"""
st.markdown(hero_html, unsafe_allow_html=True)

# =========================================================
# SESSION STATE INIT
# =========================================================

if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "knowledge" not in st.session_state:
    st.session_state.knowledge = ""
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "previous_questions" not in st.session_state:
    st.session_state.previous_questions = []
if "performance" not in st.session_state:
    st.session_state.performance = PerformanceAnalyzer()
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "result" not in st.session_state:
    st.session_state.result = None
if "explanation" not in st.session_state:
    st.session_state.explanation = ""
if "user_answer" not in st.session_state:
    st.session_state.user_answer = ""
if "quiz_finished" not in st.session_state:
    st.session_state.quiz_finished = False
if "answered_indices" not in st.session_state:
    st.session_state.answered_indices = set()
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Medium"
if "question_type" not in st.session_state:
    st.session_state.question_type = "MCQ"
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 5

# =========================================================
# LANDING / SETUP SCREEN
# =========================================================

if not st.session_state.quiz_started:

    col_left, col_right = st.columns(2, gap="medium")

    # ------------------ LEFT CARD: ADD MATERIAL ------------------
    with col_left:
        left_card_open = f"""<div class="saas-card-box">
<div class="card-title-row">
<span class="dot-indicator"></span>
<h2>Add material</h2>
</div>
<div class="card-desc">Drop in a PDF, DOCX, or image of your notes.</div>
<div class="cloud-graphic-box">
<svg width="140" height="90" viewBox="0 0 140 90" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M 28 48 A 42 42 0 0 1 112 48" stroke="{T['cloud_accent']}" stroke-width="2" stroke-dasharray="3 5" opacity="0.8" fill="none"/>
<path d="M 40 60 C 31 60 26 53 26 45 C 26 37 32 31 41 31 C 44 22 53 15 65 15 C 78 15 87 23 89 32 C 96 32 102 38 102 45 C 102 53 96 60 88 60 Z" fill="{T['cloud_bg']}" stroke="{T['cloud_stroke']}" stroke-width="2.5" stroke-linejoin="round"/>
<rect x="53" y="28" width="26" height="32" rx="4" fill="{T['surface']}" stroke="{T['cloud_stroke']}" stroke-width="2.5"/>
<path d="M 60 37 H 72 M 60 44 H 72 M 60 51 H 68" stroke="{T['cloud_stroke']}" stroke-width="2" stroke-linecap="round"/>
<path d="M 70 48 L 75 42 C 76.8 40.2 79.8 40.2 81.6 42 C 82.8 43.2 82.8 45 81.6 46.2 L 74 55 L 74 64 L 67 64 L 67 52 Z" fill="{T['cloud_accent']}" stroke="{T['surface']}" stroke-width="1.2"/>
</svg>
</div>"""
        st.markdown(left_card_open, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload Notes Document",
            type=["pdf", "docx", "png", "jpg", "jpeg"],
            label_visibility="collapsed",
            key="file_uploader_main"
        )

        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_file is not None:
            st.markdown(f'<div style="text-align: center; font-size: 13px; font-weight: 800; color: var(--accent); margin-top: 10px;">Selected File: {uploaded_file.name}</div>', unsafe_allow_html=True)

    # ------------------ RIGHT CARD: CONFIGURE QUIZ ------------------
    with col_right:
        right_card_open = """<div class="saas-card-box">
<div class="card-title-row">
<span class="dot-indicator"></span>
<h2>Configure quiz</h2>
</div>
<div class="card-desc">Choose difficulty, format, and length.</div>"""
        st.markdown(right_card_open, unsafe_allow_html=True)

        # 1. Difficulty Select Box
        st.markdown('<div class="config-group-card"><div class="config-group-header"><span class="icon">✨</span><span class="title">Difficulty</span></div>', unsafe_allow_html=True)
        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
            index=1,
            label_visibility="collapsed",
            key="diff_select_key"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. Question Type Select Box
        st.markdown('<div class="config-group-card"><div class="config-group-header"><span class="icon">📝</span><span class="title">Question Type</span></div>', unsafe_allow_html=True)
        question_type = st.selectbox(
            "Question Type",
            ["MCQ", "Short Answer", "Long Answer", "Fill in the Blanks", "True/False", "One Word"],
            index=0,
            label_visibility="collapsed",
            key="qtype_select_key"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. Number of Questions Slider Box
        st.markdown('<div class="slider-container-card"><div class="slider-lbl">Number of Questions</div>', unsafe_allow_html=True)
        num_questions = st.slider(
            "Number of Questions",
            min_value=1,
            max_value=10,
            value=5,
            label_visibility="collapsed",
            key="num_q_slider_key"
        )
        slider_meta_html = f"""<div class="slider-meta-row">
<span>1</span>
<span class="slider-meta-val">{num_questions} Questions</span>
<span>10</span>
</div>
</div>"""
        st.markdown(slider_meta_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Start Quiz Primary Button
    st.markdown('<div style="margin-top: 28px; text-align: center;">', unsafe_allow_html=True)
    start_clicked = st.button("Start Quiz", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    start_clicked = False
    uploaded_file = None

# =========================================================
# START QUIZ PROCESSOR
# =========================================================

if start_clicked:
    if uploaded_file is None:
        st.error("Please upload a study material document first.")
        st.stop()

    os.makedirs("temp", exist_ok=True)
    filepath = Path("temp") / uploaded_file.name

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Extracting document content..."):
        knowledge = extract_text(filepath)

    st.session_state.knowledge = knowledge
    st.session_state.quiz_started = True
    st.session_state.questions = []
    st.session_state.previous_questions = []
    st.session_state.current_question = 0
    st.session_state.show_result = False
    st.session_state.user_answer = ""
    st.session_state.quiz_finished = False
    st.session_state.performance = PerformanceAnalyzer()
    st.session_state.answered_indices = set()
    st.session_state.difficulty = difficulty
    st.session_state.question_type = question_type
    st.session_state.num_questions = num_questions

    st.rerun()

difficulty = st.session_state.difficulty
question_type = st.session_state.question_type
num_questions = st.session_state.num_questions

# Generate questions
if st.session_state.quiz_started and len(st.session_state.questions) == 0:
    with st.spinner("Generating questions..."):
        for _ in range(num_questions):
            quiz = generator.generate_question(
                st.session_state.knowledge,
                difficulty.lower(),
                question_type,
                st.session_state.previous_questions
            )
            st.session_state.questions.append(quiz)
            st.session_state.previous_questions.append(quiz["question"])
    st.rerun()

# =========================================================
# ACTIVE QUIZ INTERFACE
# =========================================================

if st.session_state.quiz_started and len(st.session_state.questions) > 0 and not st.session_state.quiz_finished:

    current = st.session_state.current_question
    total = len(st.session_state.questions)
    quiz = st.session_state.questions[current]

    st.progress((current) / total if total else 0)

    st.markdown('<div class="saas-card-box" style="margin-top:20px;">', unsafe_allow_html=True)
    q_header_html = f"""<div style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); margin-bottom:6px;">
Question {current + 1} of {total}
</div>
<h2 style="font-family:'Playfair Display', serif; font-size:24px; font-weight:700; margin-bottom:20px;">
{quiz["question"]}
</h2>"""
    st.markdown(q_header_html, unsafe_allow_html=True)

    qtype = quiz["question_type"]

    if qtype == "MCQ":
        answer = st.radio("Choose Answer", quiz.get("options", []), key=f"ans_radio_run_{current}")
    elif qtype == "True/False":
        answer = st.radio("Choose Option", ["True", "False"], key=f"ans_radio_run_{current}")
    elif qtype in ("Fill in the Blanks", "One Word"):
        answer = st.text_input("Your Answer", key=f"ans_text_run_{current}")
    else:
        answer = st.text_area("Write your response", height=180, key=f"ans_area_run_{current}")

    col1, col2 = st.columns(2)
    with col1:
        if current > 0:
            if st.button("Previous"):
                st.session_state.current_question -= 1
                st.session_state.show_result = False
                st.rerun()

    with col2:
        if st.button("Submit Answer", type="primary"):
            st.session_state.user_answer = answer

            with st.spinner("Evaluating answer..."):
                result = evaluator.evaluate(quiz, answer)

            if current not in st.session_state.answered_indices:
                st.session_state.performance.update(quiz, result, difficulty.lower())
                st.session_state.answered_indices.add(current)

            with st.spinner("Generating explanation..."):
                explanation = explainer.explain(quiz)

            st.session_state.result = result
            st.session_state.explanation = explanation
            st.session_state.show_result = True
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_result:
        result = st.session_state.result
        explanation = st.session_state.explanation

        st.markdown('<div class="saas-card-box" style="margin-top:20px;">', unsafe_allow_html=True)
        if result.get("correct") is True:
            st.success("Correct. Great job.")
        elif result.get("correct") is False:
            st.error("Incorrect.")
        else:
            st.info(f"Marks: {result.get('marks',0)} / {result.get('max_marks',5)}")

        st.markdown("#### Feedback")
        fb_html = f'<div style="background:var(--surface-2); border-left:4px solid var(--accent); padding:16px; border-radius:12px; font-weight:500;">{result.get("feedback","")}</div>'
        st.markdown(fb_html, unsafe_allow_html=True)

        st.markdown("#### Explanation")
        exp_html = f'<div style="background:var(--surface-2); border-left:4px solid var(--accent); padding:16px; border-radius:12px; font-weight:500;">{explanation}</div>'
        st.markdown(exp_html, unsafe_allow_html=True)

        if current < total - 1:
            if st.button("Next Question", type="primary"):
                st.session_state.current_question += 1
                st.session_state.show_result = False
                st.session_state.user_answer = ""
                st.rerun()
        else:
            st.success("Quiz Completed")
            if st.button("View Performance Dashboard", type="primary"):
                st.session_state.quiz_finished = True
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# PERFORMANCE DASHBOARD
# =========================================================

if st.session_state.get("quiz_finished", False):
    st.markdown("## Performance Dashboard")
    performance = st.session_state.performance
    total = performance.total_questions
    correct = performance.correct
    accuracy = (correct / total * 100) if total else 0

    st.markdown('<div class="saas-card-box">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Questions", total)
    c2.metric("Correct Answers", correct)
    c3.metric("Accuracy", f"{accuracy:.1f}%")
    st.progress(accuracy / 100)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top:20px; text-align:center;">', unsafe_allow_html=True)
    if st.button("Start New Quiz", type="primary"):
        st.session_state.quiz_started = False
        st.session_state.quiz_finished = False
        st.session_state.questions = []
        st.session_state.previous_questions = []
        st.session_state.current_question = 0
        st.session_state.user_answer = ""
        st.session_state.show_result = False
        st.session_state.knowledge = ""
        st.session_state.performance = PerformanceAnalyzer()
        st.session_state.answered_indices = set()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
