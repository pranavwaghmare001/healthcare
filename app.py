import streamlit as st
import pandas as pd
import os
import tempfile

from model import DiseaseModel, DISEASE_INFO
from nlp_extractor import SymptomExtractor
import data_generator
from home_care import get_home_care
from emergency import check_emergency, get_mock_hospitals
from translator import translate_text, get_supported_languages
from report_parser import parse_report
from chatbot import get_bot_response
import ui_utils

from auth import login_user, create_user
from database import save_history, get_history

import plotly.express as px
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_title="Smart Health Assistant", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")
ui_utils.inject_custom_css()

@st.cache_resource
def load_model_and_extractor():
    if not os.path.exists("dataset.csv"):
        df = data_generator.generate_synthetic_data(num_samples=2000)
        df.to_csv("dataset.csv", index=False)
    model = DiseaseModel()
    model.load_and_train("dataset.csv")
    all_symptoms = model.get_all_symptoms()
    extractor = SymptomExtractor(all_symptoms)
    return model, extractor, all_symptoms


# ─────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────
def login_signup_page():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div class='white-card' style='padding:40px; margin-top: 50px;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; font-size:2.2rem; color:#0f172a;'>Welcome Back</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; margin-bottom:30px; color:#64748b;'>Enter your clinical credentials to access the pulse dashboard.</p>", unsafe_allow_html=True)

        t_login, t_signup, t_guest = st.tabs(["Sign In", "Register", "Guest"])

        with t_login:
            with st.form("login_form"):
                user = st.text_input("EMAIL ADDRESS / USERNAME", placeholder="dr.smith@clinicalcurator.com")
                pwd = st.text_input("PASSWORD", type="password", placeholder="••••••••••••")
                col_rm, col_fp = st.columns([1, 1])
                with col_rm:
                    st.checkbox("Remember me")
                with col_fp:
                    st.markdown("<p style='text-align:right; color:#0d6efd; font-weight:500; font-size:0.9em; margin-top:8px;'>Forgot password?</p>", unsafe_allow_html=True)
                if st.form_submit_button("Sign In →", use_container_width=True):
                    success, val1, val2 = login_user(user, pwd)
                    if success:
                        st.session_state.user_id = val1
                        st.session_state.username = val2
                        st.rerun()
                    else:
                        st.error(val2)
            st.markdown("<p style='text-align:center; font-size:0.8em; color:#94a3b8; margin:20px 0;'>OR CONTINUE WITH</p>", unsafe_allow_html=True)
            col_g, col_a = st.columns(2)
            with col_g: st.button("⬛ Google", use_container_width=True)
            with col_a: st.button("🍏 Apple", use_container_width=True)

        with t_signup:
            with st.form("signup_form"):
                new_name = st.text_input("Full Name", placeholder="e.g. John Doe")
                new_age = st.number_input("Age", min_value=1, max_value=120, value=30, step=1)
                new_user = st.text_input("Username")
                new_pwd = st.text_input("Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if len(new_user) < 4 or len(new_pwd) < 6:
                        st.error("Username > 3 and Password > 5 characters required.")
                    else:
                        success, val = create_user(new_user, new_pwd, new_name, new_age)
                        if success: st.success("Account created! Please Sign In.")
                        else: st.error(val)

        with t_guest:
            st.info("Guest Mode: medical history is not saved.", icon="ℹ️")
            if st.button("Enter as Guest →", use_container_width=True):
                st.session_state.user_id = -1
                st.session_state.username = "Guest"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('''
        <div class="blue-insight-card" style="margin-top:20px; display:flex; align-items:center; gap:15px;">
            <div style="background:white; border-radius:50%; padding:10px; flex-shrink:0; min-width:40px; text-align:center;">🛡️</div>
            <div>
                <h4 style="margin:0; font-size:1.1em;">HIPAA Encrypted Session</h4>
                <p style="margin:0; font-size:0.85em; opacity:0.9;">Your data remains protected with AES-256 military-grade encryption during this clinical session.</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)


# ─────────────────────────────────────
# DIAGNOSIS PAGE
# ─────────────────────────────────────
def render_diagnosis(model, extractor, all_symptoms, target_lang):
    st.markdown("<h1 style='color:#0f172a;'>🧠 AI-Powered Smart Health Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; margin-top:-10px; margin-bottom:20px;'>Enter Patient Details to get an AI-driven clinical assessment.</p>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#0f172a; margin-bottom:16px;'>👤 Demographic Data</h4>", unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            age = st.number_input("PATIENT AGE", min_value=1, max_value=120, value=25, step=1)
        with dc2:
            gender = st.selectbox("GENDER", ["Male", "Female", "Other"])
        with dc3:
            location = st.text_input("LOCATION", placeholder="e.g. London, UK")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<div class='white-card'>", unsafe_allow_html=True)
        sym_hcol, sym_tcol = st.columns([2, 1])
        with sym_hcol:
            st.markdown("<h4 style='color:#0f172a;'>🩺 Symptoms & Manifestations</h4>", unsafe_allow_html=True)
        with sym_tcol:
            input_mode = st.radio("", ["List", "Natural Language", "Voice"], horizontal=True, label_visibility="collapsed")

        selected_symptoms = []
        if input_mode == "Natural Language":
            user_text = st.text_area("Describe your symptoms:", placeholder="e.g., I have a severe headache and fever since yesterday.", label_visibility="collapsed")
            if user_text:
                extracted = extractor.extract_symptoms(user_text)
                if extracted:
                    st.success(f"**Extracted Symptoms:** {', '.join(extracted)}")
                    selected_symptoms = extracted
                else:
                    st.warning("No recognized symptoms found. Try selecting from the list.")
        elif input_mode == "Voice":
            st.markdown("🎙️ Click the mic to record your symptoms:")
            audio_bytes = audio_recorder()
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                with st.spinner("Transcribing..."):
                    r = sr.Recognizer()
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
                            fp.write(audio_bytes)
                            tmp_name = fp.name
                        with sr.AudioFile(tmp_name) as source:
                            audio_data = r.record(source)
                        text = r.recognize_google(audio_data)
                        st.write(f"**Transcription:** {text}")
                        extracted = extractor.extract_symptoms(text)
                        if extracted:
                            st.success(f"**Extracted Symptoms:** {', '.join(extracted)}")
                            selected_symptoms = extracted
                        else:
                            st.warning("No recognized symptoms found from the audio.")
                    except sr.UnknownValueError:
                        st.error("Audio not understood.")
                    except Exception as e:
                        st.error(f"Error processing audio: {e}")
        else:
            selected_symptoms = st.multiselect("Select your symptoms:", options=all_symptoms, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        diagnose_clicked = st.button("📊 Analyze Symptoms", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if "last_results" not in st.session_state:
        st.session_state.last_results = None
        st.session_state.last_care_tips = None
        st.session_state.last_emergency = False
        st.session_state.last_critical = []
        st.session_state.last_location = ""

    if diagnose_clicked:
        if not selected_symptoms:
            st.session_state.last_results = None
            st.error("Please provide at least one symptom.")
        else:
            with st.spinner("Analyzing symptoms..."):
                results, _ = model.predict(selected_symptoms)
            is_emergency, critical_symptoms = check_emergency(selected_symptoms)
            if is_emergency and results:
                results[0]["severity"] = "High"
            care_tips = get_home_care(results[0]["disease"], results[0]["severity"], age) if results else None
            st.session_state.last_results = results
            st.session_state.last_care_tips = care_tips
            st.session_state.last_emergency = is_emergency
            st.session_state.last_critical = critical_symptoms
            st.session_state.last_location = location
            if results:
                save_history(st.session_state.user_id, 'prediction', {
                    'symptoms': selected_symptoms,
                    'top_disease': results[0]['disease'],
                    'probability': results[0]['probability'],
                    'severity': results[0]['severity']
                })

    results = st.session_state.last_results
    is_emergency = st.session_state.last_emergency
    critical_symptoms = st.session_state.last_critical
    loc = st.session_state.last_location
    care_tips = st.session_state.last_care_tips

    with col_right:
        if results:
            top = results[0]
            severity_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}.get(top["severity"], "#64748b")
            st.markdown(f"""
            <div class="white-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                    <h3 style="color:#0d6efd; margin:0;">{translate_text(top['disease'], target_lang)}</h3>
                    <span style="background:#d1fae5; color:#065f46; font-size:0.7em; font-weight:700; padding:4px 10px; border-radius:20px; white-space:nowrap;">AI RESULT</span>
                </div>
                <p style="color:#64748b; font-size:0.85em; margin-bottom:4px;">Confidence Match <strong style="float:right;">{top['probability']}%</strong></p>
                <div style="background:#e2e8f0; border-radius:4px; height:8px; margin-bottom:12px;">
                    <div style="background:#0d6efd; width:{top['probability']}%; height:8px; border-radius:4px;"></div>
                </div>
                <span style="background:{severity_color}22; color:{severity_color}; font-size:0.8em; font-weight:600; padding:3px 10px; border-radius:20px;">
                    ⬤ {top['severity']} Severity
                </span>
                <p style="color:#475569; font-size:0.85em; margin-top:12px;">{top.get('advice', 'Based on reported symptoms, a clinical assessment is recommended.')}</p>
            </div>
            """, unsafe_allow_html=True)

            if len(results) > 1:
                with st.expander("View all predictions"):
                    for idx, res in enumerate(results[1:], 2):
                        st.markdown(f"**{idx}. {translate_text(res['disease'], target_lang)}** — {res['probability']}%")
                        st.progress(int(res['probability']))

            if care_tips:
                st.markdown(f"""
                <div style="background:#eff6ff; border-radius:12px; padding:20px; margin-top:16px;">
                    <p style="color:#0d6efd; font-size:0.75em; font-weight:700; letter-spacing:1px; margin-bottom:10px;">RECOMMENDED SUGGESTIONS</p>
                    <p style="margin:6px 0; color:#1e3a5f;">✅ {translate_text(care_tips['diet'], target_lang)}</p>
                    <p style="margin:6px 0; color:#1e3a5f;">✅ {translate_text(care_tips['remedies'], target_lang)}</p>
                    <p style="margin:6px 0; color:#1e3a5f;">✅ Stay hydrated and monitor vital signs regularly.</p>
                </div>
                """, unsafe_allow_html=True)

            probs = [r['probability'] for r in results]
            diseases_list = [translate_text(r['disease'], target_lang) for r in results]
            if sum(probs) < 100:
                probs.append(100 - sum(probs))
                diseases_list.append("Other")
            fig = px.pie(values=probs, names=diseases_list, hole=0.45,
                         color_discrete_sequence=["#0d6efd", "#60a5fa", "#93c5fd", "#bfdbfe"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color="#334155"), showlegend=True, margin=dict(t=20, b=20),
                              title=dict(text="Probability Breakdown", font=dict(color="#0f172a")))
            st.plotly_chart(fig, use_container_width=True)

        if is_emergency:
            hospitals_html = "".join([f"<li>🏥 {h['name']} ({h['distance']}, ~{h['time']})</li>" for h in get_mock_hospitals(loc)])
            st.markdown(f"""
            <div class="emergency-alert-card" style="margin-top:16px;">
                <p style="font-weight:700; margin:0 0 8px 0;">🚨 EMERGENCY ALERT</p>
                <p style="margin:0 0 8px 0;">Critical: <strong>{', '.join(critical_symptoms)}</strong>. Call emergency services immediately.</p>
                <ul style="margin:0; padding-left:18px;">{hospitals_html}</ul>
            </div>
            """, unsafe_allow_html=True)
            st.button("📞 CALL AMBULANCE (108)", use_container_width=True)

        st.markdown("""
        <div class="disclaimer-card" style="margin-top:16px;">
            <span style="font-size:1.5em;">🔇</span>
            <div><strong>Medical Disclaimer</strong><br>For informational purposes only. Consult a licensed medical professional for formal diagnosis.</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────
# REPORT SCANNER PAGE
# ─────────────────────────────────────
STATUS_COLOR = {
    "Normal":   "#22c55e",
    "Low":      "#f59e0b",
    "High":     "#ef4444",
    "Critical": "#dc2626",
    "Elevated": "#f97316",
    "Optimal":  "#3b82f6",
    "Stable":   "#22c55e",
    "Recorded": "#64748b",
}

def render_report(target_lang):
    st.markdown("<h1 style='color:#0f172a;'>📄 Medical Report Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; margin-top:-10px; margin-bottom:20px;'>AI-powered extraction and clinical interpretation of your medical documents using WHO standard reference ranges.</p>", unsafe_allow_html=True)

    col_upload, col_metrics = st.columns([3, 2], gap="large")

    parsed_data = None
    uploaded_file = None

    with col_upload:
        st.markdown("""
        <div class="white-card" style="border:2px dashed #cbd5e1; text-align:center; padding:40px;">
            <div style="font-size:2.5em; margin-bottom:10px;">☁️</div>
            <h3 style="color:#0f172a;">Drag and Drop Report</h3>
            <p style="color:#64748b;">PDF, JPG, PNG, TXT — up to 25MB.<br>High-resolution scans recommended for best OCR accuracy.</p>
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload Report",
            type=["pdf", "txt", "png", "jpg", "jpeg", "bmp", "tiff"],
            label_visibility="collapsed"
        )

        if uploaded_file:
            with st.spinner("🔬 Running AI extraction and clinical analysis..."):
                parsed_data, error = parse_report(uploaded_file)

            if error:
                st.error(f"⚠️ {error}")
                parsed_data = None
            elif parsed_data:
                metrics = parsed_data.get("metrics", {})
                fallback = parsed_data.get("fallback_lines", [])
                if not metrics and not fallback:
                    st.warning("No structured biomarkers detected. Try a clearer, higher-resolution scan.")
                    parsed_data = None
                else:
                    st.success(f"✅ **{len(metrics)} biomarker(s)** extracted and clinically interpreted.")
                    with st.expander("📄 View raw document / OCR text"):
                        st.code(parsed_data.get("raw_text", ""), language=None)
                    if fallback and not metrics:
                        st.markdown("**Raw detected lines (unstructured):**")
                        for line in fallback:
                            st.markdown(f"- `{line}`")

    with col_metrics:
        if parsed_data and parsed_data.get("metrics"):
            metrics = parsed_data["metrics"]

            st.markdown("<div class='white-card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#0f172a; margin-bottom:16px;'>📊 Extracted Metrics</h4>", unsafe_allow_html=True)

            for biomarker, info in metrics.items():
                val    = info.get("value", "—")
                status = info.get("status", "Recorded")
                color  = STATUS_COLOR.get(status, "#64748b")
                st.markdown(f"""
                <div style="background:#f8fafc; border-radius:10px; padding:14px; margin-bottom:10px; border-left:4px solid {color};">
                    <p style="color:#64748b; font-size:0.7em; font-weight:700; letter-spacing:1px; margin:0 0 4px 0;">{biomarker.upper()}</p>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:1.5em; font-weight:700; color:#0f172a;">{val}</span>
                        <span style="background:{color}22; color:{color}; font-size:0.75em; font-weight:600; padding:2px 10px; border-radius:20px; white-space:nowrap;">{status}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # AI Insights from clinical interpretation messages
            abnormal = [
                info["message"]
                for info in metrics.values()
                if info.get("status") not in ("Normal", "Optimal", "Stable", "Recorded") and info.get("message")
            ]
            if abnormal:
                insights_html = "".join([f"<li style='margin:8px 0;'>⚠️ {msg}</li>" for msg in abnormal])
                severity_label = "⚡ Action Required" if any(
                    info.get("status") in ("High", "Critical") for info in metrics.values()
                ) else "💡 Review Advised"
            else:
                insights_html = "<li>✅ All scanned biomarkers are within healthy reference ranges.</li>"
                severity_label = "✅ All Clear"

            st.markdown(f"""
            <div class="blue-insight-card" style="margin-top:16px;">
                <p style="color:rgba(255,255,255,0.7); font-size:0.7em; font-weight:700; letter-spacing:1px; margin-bottom:4px;">✨ AI INSIGHTS</p>
                <p style="color:white; font-weight:600; font-size:0.9em; margin-bottom:12px;">{severity_label}</p>
                <ul style="padding-left:18px; margin:0; color:white;">{insights_html}</ul>
            </div>
            """, unsafe_allow_html=True)

            save_history(st.session_state.user_id, 'report', {
                'filename': uploaded_file.name,
                'metrics': {k: v.get("value") for k, v in metrics.items()},
                'insights_triggered': len(abnormal)
            })
        else:
            st.markdown("""
            <div class="white-card" style="text-align:center; padding:40px; color:#94a3b8;">
                <div style="font-size:2em; margin-bottom:8px;">📋</div>
                <p>Upload a report to see AI-interpreted metrics here.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#eff6ff; border-radius:12px; padding:20px; margin-top:24px; display:flex; align-items:center; gap:12px;">
        <span style="font-size:1.5em;">🛡️</span>
        <div>
            <strong style="color:#0f172a;">HIPAA Compliant &amp; Encrypted</strong><br>
            <span style="color:#64748b; font-size:0.85em;">Medical data is processed with AES-256 encryption. Raw files are not stored after synthesis.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────
# HISTORY PAGE
# ─────────────────────────────────────
def render_history():
    st.markdown("<h1 style='color:#0f172a;'>📚 Medical History Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; margin-top:-10px; margin-bottom:20px;'>Your persistent clinical timeline, fetched securely from the cloud.</p>", unsafe_allow_html=True)

    if st.session_state.user_id == -1:
        st.warning("You are browsing in Guest Mode. Create an account to enable history tracking.", icon="⚠️")
        return

    records = get_history(st.session_state.user_id)
    if not records:
        st.info("Your medical timeline is empty. Run a Diagnosis or upload a Lab Report to get started.", icon="ℹ️")
        return

    for rec in records:
        icon = "🩺" if rec['type'] == 'prediction' else "📄"
        with st.expander(f"{icon} {rec['type'].upper()} — {rec['time']}"):
            if rec['type'] == 'prediction':
                sev = rec['data'].get('severity', '')
                sev_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}.get(sev, "#64748b")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**🦠 Predicted Disease:** {rec['data']['top_disease']}")
                    st.markdown(f"**Confidence:** {rec['data']['probability']}%")
                    st.progress(int(rec['data']['probability']))
                with col2:
                    st.markdown(f"**Severity:** <span style='color:{sev_color}; font-weight:600;'>{sev}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Symptoms:** {', '.join(rec['data']['symptoms'])}")
            elif rec['type'] == 'report':
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**📁 File:** `{rec['data']['filename']}`")
                with c2:
                    st.markdown(f"**⚠️ Clinical Flags:** {rec['data'].get('insights_triggered', 0)}")
                if 'metrics' in rec['data']:
                    st.json(rec['data']['metrics'])


# ─────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────
def main():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
        st.session_state.username = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.session_state.user_id is None:
        login_signup_page()
        return

    # Sidebar
    st.sidebar.markdown(f"""
    <div style="padding:16px 0 10px 0;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
            <div style="width:40px; height:40px; border-radius:50%; background:#0d6efd; display:flex; align-items:center; justify-content:center; color:white; font-weight:700; font-size:1.1em; flex-shrink:0;">
                {st.session_state.username[0].upper()}
            </div>
            <div>
                <p style="margin:0; font-weight:600; color:#0f172a;">{st.session_state.username}</p>
                <p style="margin:0; font-size:0.75em; color:#64748b;">Clinical Dashboard</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("⏻  Log Out", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.last_results = None
        st.session_state.chat_history = []
        st.rerun()

    with st.spinner("Loading Medical Core Models..."):
        try:
            model, extractor, all_symptoms = load_model_and_extractor()
        except Exception as e:
            st.error(f"Error loading systems: {e}")
            st.stop()

    langs = get_supported_languages()
    target_lang_name = st.sidebar.selectbox("🌐 Language", list(langs.keys()))
    target_lang = langs[target_lang_name]

    st.sidebar.divider()
    nav = st.sidebar.radio("", [
        "🩺 Diagnosis & Emergency",
        "💬 AI Chatbot",
        "📄 Medical Report Scan",
        "📚 Lab History",
        "🔍 Disease Lookup",
    ], index=0, label_visibility="collapsed")

    st.sidebar.divider()
    if st.sidebar.button("＋  New Consultation", use_container_width=True):
        st.session_state.last_results = None
        st.session_state.chat_history = []
        st.rerun()

    if nav == "🩺 Diagnosis & Emergency":
        render_diagnosis(model, extractor, all_symptoms, target_lang)

    elif nav == "📄 Medical Report Scan":
        render_report(target_lang)

    elif nav == "📚 Lab History":
        render_history()

    elif nav == "💬 AI Chatbot":
        st.markdown("<h1 style='color:#0f172a;'>💬 AI Consultation</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b; margin-top:-10px; margin-bottom:20px;'>Ask about symptoms, medications, or get a second opinion on your diagnosis.</p>", unsafe_allow_html=True)

        chat_col, _ = st.columns([3, 1])
        with chat_col:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            user_msg = st.chat_input("Ask me about health tips or specific symptoms...")
            if user_msg:
                st.session_state.chat_history.append({"role": "user", "content": user_msg})
                with st.chat_message("user"): st.markdown(user_msg)
                with st.spinner("AI is thinking..."):
                    ans = translate_text(get_bot_response(user_msg, all_symptoms), target_lang)
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
                with st.chat_message("assistant"): st.markdown(ans)

    elif nav == "🔍 Disease Lookup":
        st.markdown("<h1 style='color:#0f172a;'>🔍 Disease Lookup</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b; margin-top:-10px; margin-bottom:20px;'>Search the clinical knowledge database for disease information.</p>", unsafe_allow_html=True)

        search_query = st.text_input("Search disease (e.g. Malaria, Dengue, Diabetes):")
        if search_query:
            df = pd.read_csv("dataset.csv")
            matches = df[df["Disease"].str.lower().str.contains(search_query.lower())]
            if not matches.empty:
                st.success(f"Found {len(matches)} variant(s) for '{search_query}'.")
                disease_name = matches.iloc[0]["Disease"]
                info = DISEASE_INFO.get(disease_name, None)
                sev_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}.get(info['severity'] if info else '', "#64748b")

                col_info, col_syms = st.columns([1, 1], gap="large")
                with col_info:
                    if info:
                        st.markdown(f"""
                        <div class="white-card">
                            <h3 style="color:#0d6efd;">{disease_name}</h3>
                            <span style="background:{sev_color}22; color:{sev_color}; padding:3px 10px; border-radius:20px; font-weight:600; font-size:0.85em;">
                                ⬤ {info['severity']} Severity
                            </span>
                            <hr style="border-color:#f1f5f9; margin:12px 0;">
                            <p style="color:#475569;"><strong>Care Plan:</strong><br>{info['advice']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                with col_syms:
                    syms = [col for col in df.columns if col != "Disease" and matches.iloc[0][col] == 1]
                    st.markdown("<div class='white-card'><h4 style='color:#0f172a; margin-bottom:12px;'>Common Symptoms</h4>", unsafe_allow_html=True)
                    for sym in syms:
                        st.markdown(f"🔹 {sym.replace('_', ' ').title()}")
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(f"'{search_query}' not found in the knowledge base.")


if __name__ == "__main__":
    main()
