import streamlit as st

def inject_custom_css():
    st.markdown("""
<style>
/* ─────────────── FONTS ─────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ─────────────── APP BACKGROUND ─────────────── */
[data-testid="stAppViewContainer"] {
    background: #f0f4f8;
}
[data-testid="stHeader"] {
    background: transparent !important;
}
/* Remove default top padding on main block */
.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1280px;
}

/* ─────────────── SIDEBAR ─────────────── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    padding-top: 1rem;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.85rem;
    color: #64748b;
}
/* Sidebar nav radio buttons — style like a real nav menu */
[data-testid="stSidebar"] .stRadio > label {
    display: none;
}
[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    display: flex;
    align-items: center;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 0.9rem;
    font-weight: 500;
    color: #475569;
    cursor: pointer;
    transition: background 0.15s ease, color 0.15s ease;
    width: 100%;
    margin-bottom: 2px;
    border: none;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: #eff6ff;
    color: #0d6efd;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"],
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
    background: #eff6ff;
    color: #0d6efd;
    font-weight: 600;
}
/* Hide the actual radio circle */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span:first-child {
    display: none !important;
}
/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: #f1f5f9;
    margin: 12px 0;
}

/* ─────────────── TYPOGRAPHY ─────────────── */
h1 { font-size: 1.85rem !important; font-weight: 800 !important; color: #0f172a !important; letter-spacing: -0.5px; margin-bottom: 0.3rem !important; }
h2 { font-size: 1.4rem !important; font-weight: 700 !important; color: #0f172a !important; }
h3 { font-size: 1.1rem !important; font-weight: 700 !important; color: #0f172a !important; }
h4 { font-size: 0.95rem !important; font-weight: 700 !important; color: #0f172a !important; }
p  { color: #475569; line-height: 1.65; }

/* Force white text on ALL buttons (including nested span/p) */
div.stButton > button, 
div.stButton > button p, 
div.stButton > button span,
div.stButton > button div {
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
}

div.stButton > button {
    background: #0d6efd !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.6rem !important;
    text-shadow: 0px 1px 2px rgba(0,0,0,0.15) !important;
    box-shadow: 0 2px 8px rgba(13,110,253,0.25) !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em;
}

div.stButton > button:hover {
    background: #0b5ed7 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(13,110,253,0.35) !important;
}

div.stButton > button:active {
    transform: translateY(0) !important;
}

/* ─────────────── INPUTS ─────────────── */
input, textarea, select {
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    padding: 0.5rem 0.75rem !important;
    color: #0f172a !important;
    transition: border-color 0.15s ease !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #0d6efd !important;
    box-shadow: 0 0 0 3px rgba(13,110,253,0.1) !important;
}
/* Selectbox */
[data-baseweb="select"] > div {
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 8px !important;
}
/* Label above inputs */
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    color: #94a3b8 !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}
/* Multiselect tags */
[data-baseweb="tag"] {
    background: #eff6ff !important;
    border-radius: 6px !important;
}
[data-baseweb="tag"] span {
    color: #0d6efd !important;
    font-weight: 600 !important;
}

/* ─────────────── TABS ─────────────── */
[data-baseweb="tab-list"] {
    gap: 4px;
    background: #f1f5f9 !important;
    border-radius: 10px;
    padding: 4px;
    border: none !important;
}
button[data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #64748b !important;
    font-weight: 500 !important;
    padding: 6px 18px !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.15s ease !important;
}
button[data-baseweb="tab"]:hover {
    background: #e2e8f0 !important;
    color: #334155 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: #ffffff !important;
    color: #0d6efd !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
}

/* ─────────────── EXPANDERS ─────────────── */
div[data-testid="stExpander"] {
    background: #ffffff;
    border-radius: 12px !important;
    border: 1.5px solid #e2e8f0 !important;
    margin-bottom: 12px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
div[data-testid="stExpander"] > details > summary {
    background: #ffffff;
    padding: 14px 18px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: #0f172a !important;
}
div[data-testid="stExpander"] > details > summary:hover {
    background: #f8fafc;
}
div[data-testid="stExpander"] > details[open] > summary {
    border-bottom: 1.5px solid #f1f5f9;
}

/* ─────────────── CHAT MESSAGES ─────────────── */
div[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 1rem 1.25rem;
    margin-bottom: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

/* ─────────────── ALERTS ─────────────── */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.9rem !important;
}

/* ─────────────── SPINNER ─────────────── */
[data-testid="stSpinner"] > div {
    color: #0d6efd;
}

/* ─────────────── PROGRESS BAR ─────────────── */
[data-testid="stProgressBar"] > div > div {
    background: #0d6efd !important;
    border-radius: 999px !important;
}
[data-testid="stProgressBar"] > div {
    background: #e2e8f0 !important;
    border-radius: 999px !important;
    height: 6px !important;
}

/* ─────────────── FILE UPLOADER ─────────────── */
[data-testid="stFileUploaderDropzone"] {
    background: #f8fafc !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 24px !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #0d6efd !important;
    background: #eff6ff !important;
}

/* ─────────────── CHECKBOX ─────────────── */
[data-testid="stCheckbox"] label {
    color: #475569 !important;
    font-size: 0.9rem !important;
    font-weight: 400 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}

/* ─────────────── METRICS ─────────────── */
div[data-testid="stMetricValue"] {
    font-size: 1.7rem !important;
    font-weight: 800 !important;
    color: #0f172a !important;
}
div[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    text-transform: uppercase;
    font-size: 0.7rem !important;
    letter-spacing: 0.8px;
    font-weight: 600 !important;
}
div[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* ─────────────── CUSTOM CARD CLASSES ─────────────── */
.white-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px 28px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04), 0 4px 20px rgba(0,0,0,0.03);
    border: 1.5px solid #f1f5f9;
    margin-bottom: 20px;
}
.white-card h4 {
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    margin-bottom: 16px !important;
}

.blue-insight-card {
    background: linear-gradient(135deg, #1d6fe8 0%, #0046cc 100%);
    color: white;
    border-radius: 16px;
    padding: 22px 24px;
    box-shadow: 0 4px 16px rgba(13,110,253,0.25);
}
.blue-insight-card h3,
.blue-insight-card h4,
.blue-insight-card p,
.blue-insight-card li,
.blue-insight-card strong {
    color: white !important;
}

.emergency-alert-card {
    background: #fff5f5;
    border-left: 4px solid #ef4444;
    border-radius: 10px;
    padding: 16px 20px;
    color: #b91c1c;
    font-size: 0.9rem;
}

.disclaimer-card {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    padding: 14px 18px;
    border-radius: 10px;
    color: #64748b;
    font-size: 0.82rem;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    line-height: 1.5;
}

/* ─────────────── PAGE SUBTITLE ─────────────── */
.page-subtitle {
    color: #64748b;
    font-size: 0.9rem;
    margin-top: -8px;
    margin-bottom: 24px;
}

/* ─────────────── HIDE streamlit footer / menu ─────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
</style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Render a consistent page header with optional subtitle."""
    st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p class='page-subtitle'>{subtitle}</p>", unsafe_allow_html=True)


def section_card(content_fn, *args, **kwargs):
    """Wraps content in a white card div."""
    st.markdown("<div class='white-card'>", unsafe_allow_html=True)
    content_fn(*args, **kwargs)
    st.markdown("</div>", unsafe_allow_html=True)
