import streamlit as st

def inject_custom_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Base Font and overall Background */
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif !important;
}

/* App Background: Very Light Gray */
[data-testid="stAppViewContainer"] {
    background: #f4f7f8;
    color: #334155;
}

/* Sidebar styling: Solid White with minimal border */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0;
}

/* Typography Overrides */
h1, h2, h3, h4, h5 {
    color: #0f172a;
    font-weight: 700;
}
p, span, label {
    color: #475569;
}

/* Premium Primary Buttons */
div.stButton > button:first-child {
    background: #0d6efd;
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    box-shadow: 0 4px 10px rgba(13, 110, 253, 0.2);
    transition: all 0.2s ease;
}

div.stButton > button:first-child:hover {
    background: #0b5ed7;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 6px 15px rgba(13, 110, 253, 0.3);
}

/* Form and Input styling - Light Theme Cards */
div[data-testid="stNumberInput"] > div, 
div[data-testid="stTextInput"] > div, 
div[data-testid="stTextArea"] > div, 
div[data-testid="stSelectbox"] > div[data-baseweb="select"] {
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    background: #f8fafc;
    color: #0f172a;
}

/* Native Streamlit Containers -> Convert to Cards */
[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    border: 1px solid #f1f5f9;
}

/* Expanders -> Look like Cards */
div[data-testid="stExpander"] {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    margin-bottom: 1rem;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}
div[data-testid="stExpander"] > details > summary {
    background: #ffffff;
    padding: 1rem;
    font-weight: 600;
    color: #0f172a;
}

/* Tabs Styling */
button[data-baseweb="tab"] {
    background: transparent;
    color: #64748b !important;
    border: none;
    font-weight: 500;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #0d6efd !important;
    border-bottom: 2px solid #0d6efd;
    font-weight: 600;
}

/* Chat Message Styling */
div[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* Metrics */
div[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 700;
    color: #0d1117;
}
div[data-testid="stMetricLabel"] {
    color: #64748b;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

/* Alerts Overrides */
div[data-testid="stAlert"] {
    border-radius: 8px;
}

/* Custom CSS Classes for HTML injection */
.blue-insight-card {
    background: linear-gradient(135deg, #0d6efd 0%, #0056b3 100%);
    color: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 6px 12px rgba(13, 110, 253, 0.2);
}
.blue-insight-card h3, .blue-insight-card p, .blue-insight-card li {
    color: white !important;
}

.emergency-alert-card {
    background: #fef2f2;
    border-left: 4px solid #ef4444;
    padding: 16px;
    border-radius: 8px;
    color: #991b1b;
}

.disclaimer-card {
    background: #f1f5f9;
    padding: 16px;
    border-radius: 8px;
    color: #475569;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 12px;
}

.white-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    border: 1px solid #e2e8f0;
    margin-bottom: 20px;
}
</style>
    """, unsafe_allow_html=True)

def structured_card_header(title, icon="⚕️"):
    st.markdown(f"<h3 style='margin-bottom: 0.5rem;'>{icon} {title}</h3>", unsafe_allow_html=True)
