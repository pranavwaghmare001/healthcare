import re
import io
import os

# ── Optional dependency imports ──────────────────────────────────────────────
try:
    import PyPDF2
    PDF_SUPPORTED = True
except ImportError:
    PDF_SUPPORTED = False

try:
    import pytesseract
    from PIL import Image, ImageFilter, ImageEnhance
    OCR_SUPPORTED = True
except ImportError:
    OCR_SUPPORTED = False


# ── Clinical Normal Ranges (WHO / standard adult references) ─────────────────
NORMAL_RANGES = {
    "Hemoglobin (Hb)": {
        "unit": "g/dL",
        "male":   (13.5, 17.5),
        "female": (12.0, 15.5),
        "default":(12.0, 17.5),
        "low_msg":  "Low Hemoglobin — possible anemia. Consider iron/B12 supplementation.",
        "high_msg": "High Hemoglobin — may indicate dehydration or polycythemia.",
    },
    "White Blood Cells (WBC)": {
        "unit": "×10³/µL",
        "default": (4.5, 11.0),
        "scale_threshold": 100,   # values > threshold are in raw cells/µL, divide by 1000
        "low_msg":  "Low WBC (leukopenia) — immune suppression risk. Consult physician.",
        "high_msg": "High WBC — suggests active infection, inflammation, or leukemia risk.",
    },
    "Red Blood Cells (RBC)": {
        "unit": "×10⁶/µL",
        "male":   (4.7, 6.1),
        "female": (4.2, 5.4),
        "default": (4.2, 6.1),
        "low_msg":  "Low RBC — may indicate anemia or blood loss.",
        "high_msg": "High RBC — may indicate dehydration or polycythemia.",
    },
    "Platelet Count": {
        "unit": "×10³/µL",
        "default": (150.0, 400.0),
        "scale_threshold": 3000,
        "low_msg":  "Thrombocytopenia — low platelets impair clotting. Seek medical advice.",
        "high_msg": "Thrombocytosis — elevated platelets may increase clot risk.",
    },
    "PCV / Hematocrit": {
        "unit": "%",
        "male":   (40.7, 50.3),
        "female": (36.1, 44.3),
        "default": (36.0, 50.0),
        "low_msg":  "Low Hematocrit — consistent with anemia.",
        "high_msg": "High Hematocrit — may indicate dehydration.",
    },
    "ESR": {
        "unit": "mm/hr",
        "male":   (0.0, 15.0),
        "female": (0.0, 20.0),
        "default": (0.0, 20.0),
        "low_msg":  None,
        "high_msg": "Elevated ESR — indicates inflammation, infection, or autoimmune disorder.",
    },
    "Glucose / Blood Sugar": {
        "unit": "mg/dL",
        "default": (70.0, 100.0),   # fasting reference
        "low_msg":  "Hypoglycemia — blood sugar dangerously low. Eat carbs immediately.",
        "high_msg": "Hyperglycemia — elevated glucose. Screen for diabetes.",
    },
    "Cholesterol (Total)": {
        "unit": "mg/dL",
        "default": (0.0, 200.0),
        "low_msg":  None,
        "high_msg": "High cholesterol — cardiovascular risk elevated. Diet and exercise advised.",
    },
    "LDL Cholesterol": {
        "unit": "mg/dL",
        "default": (0.0, 100.0),
        "low_msg":  None,
        "high_msg": "High LDL ('bad' cholesterol) — increases atherosclerosis risk.",
    },
    "HDL Cholesterol": {
        "unit": "mg/dL",
        "default": (40.0, 999.0),   # higher is better
        "low_msg":  "Low HDL ('good' cholesterol) — increases cardiovascular risk.",
        "high_msg": None,
    },
    "Triglycerides": {
        "unit": "mg/dL",
        "default": (0.0, 150.0),
        "low_msg":  None,
        "high_msg": "High triglycerides — risk for pancreatitis and heart disease.",
    },
    "Creatinine": {
        "unit": "mg/dL",
        "male":   (0.74, 1.35),
        "female": (0.59, 1.04),
        "default": (0.6, 1.4),
        "low_msg":  "Low creatinine — may indicate muscle wasting or malnutrition.",
        "high_msg": "High creatinine — possible kidney dysfunction. Urgently consult nephrologist.",
    },
    "Urea / BUN": {
        "unit": "mg/dL",
        "default": (7.0, 20.0),
        "low_msg":  "Low BUN — possible liver disease or overhydration.",
        "high_msg": "Elevated BUN — kidney disease or dehydration possible.",
    },
    "Uric Acid": {
        "unit": "mg/dL",
        "male":   (3.4, 7.0),
        "female": (2.4, 6.0),
        "default": (2.4, 7.0),
        "low_msg":  None,
        "high_msg": "High uric acid — risk for gout and kidney stones.",
    },
    "Sodium": {
        "unit": "mEq/L",
        "default": (136.0, 145.0),
        "low_msg":  "Hyponatremia — low sodium. Risk of brain swelling.",
        "high_msg": "Hypernatremia — high sodium. Often due to dehydration.",
    },
    "Potassium": {
        "unit": "mEq/L",
        "default": (3.5, 5.0),
        "low_msg":  "Hypokalemia — low potassium. Risk of muscle cramps and cardiac arrhythmia.",
        "high_msg": "Hyperkalemia — high potassium. Can cause dangerous heart rhythms.",
    },
    "Heart Rate / Pulse": {
        "unit": "bpm",
        "default": (60.0, 100.0),
        "low_msg":  "Bradycardia — heart rate below normal. May require cardiac evaluation.",
        "high_msg": "Tachycardia — elevated heart rate. Could indicate fever, anxiety, or heart condition.",
    },
    "Oxygen Saturation (SpO2)": {
        "unit": "%",
        "default": (95.0, 100.0),
        "low_msg":  "Low SpO2 — possible respiratory distress. Seek immediate medical attention.",
        "high_msg": None,
    },
    "Body Temperature": {
        "unit": "°C",
        "default": (36.1, 37.2),
        "low_msg":  "Hypothermia — body temperature dangerously low.",
        "high_msg": "Fever detected — possible infection or inflammatory response.",
    },
}

# ── Extraction patterns (label → regex capturing numeric value) ──────────────
EXTRACT_PATTERNS = {
    "Hemoglobin (Hb)":        r"(?i)(h(?:ae?|e)moglobin|HGB|Hb)\b[\s:=\-|]*([\d]{1,2}(?:\.\d+)?)\s*(?:g/?dL|g/dl)?",
    "White Blood Cells (WBC)": r"(?i)(WBC|TLC|W\.B\.C|leukocyte|white\s+blood\s+cell)s?\b[\s:=\-|]*([\d,]{2,7}(?:\.\d+)?)\s*(?:×10[³^3]|x10[³^3]|K/µL|10\^3)?",
    "Red Blood Cells (RBC)":   r"(?i)(RBC|R\.B\.C|red\s+blood\s+cell)s?\b[\s:=\-|]*([\d]{1,2}(?:\.\d+)?)\s*(?:×10[⁶^6]|x10[⁶^6]|M/µL)?",
    "Platelet Count":          r"(?i)(platelet|PLT|thrombocyte)s?\b[\s:=\-|]*([\d,]{2,7}(?:\.\d+)?)\s*(?:×10[³^3]|x10[³^3]|K/µL)?",
    "PCV / Hematocrit":        r"(?i)(PCV|hematocrit|haematocrit|HCT)\b[\s:=\-|]*([\d]{2,3}(?:\.\d+)?)\s*%?",
    "ESR":                     r"(?i)(ESR|erythrocyte\s+sediment(?:ation)?(?:\s+rate)?)\b[\s:=\-|]*([\d]{1,3}(?:\.\d+)?)\s*(?:mm/hr|mm/h)?",
    "Glucose / Blood Sugar":   r"(?i)(blood\s+glucose|glucose|FBS|RBS|fasting\s+blood\s+sugar|blood\s+sugar)\b[\s:=\-|]*([\d]{2,4}(?:\.\d+)?)\s*(?:mg/?dL|mg/dl|mmol)?",
    "Cholesterol (Total)":     r"(?i)(total\s+cholesterol|cholesterol)\b[\s:=\-|]*([\d]{2,4}(?:\.\d+)?)\s*(?:mg/?dL|mg/dl)?",
    "LDL Cholesterol":         r"(?i)(LDL(?:\s+cholesterol)?|low.?density\s+lipoprotein)\b[\s:=\-|]*([\d]{2,4}(?:\.\d+)?)\s*(?:mg/?dL|mg/dl)?",
    "HDL Cholesterol":         r"(?i)(HDL(?:\s+cholesterol)?|high.?density\s+lipoprotein)\b[\s:=\-|]*([\d]{2,4}(?:\.\d+)?)\s*(?:mg/?dL|mg/dl)?",
    "Triglycerides":           r"(?i)(triglyceride)s?\b[\s:=\-|]*([\d]{2,4}(?:\.\d+)?)\s*(?:mg/?dL|mg/dl)?",
    "Creatinine":              r"(?i)(creatinine|serum\s+creatinine)\b[\s:=\-|]*([\d]{1}(?:\.\d+)?)\s*(?:mg/?dL|mg/dl)?",
    "Urea / BUN":              r"(?i)(urea|BUN|blood\s+urea\s+nitrogen)\b[\s:=\-|]*([\d]{1,3}(?:\.\d+)?)\s*(?:mg/?dL|mg/dl)?",
    "Uric Acid":               r"(?i)(uric\s+acid|serum\s+urate)\b[\s:=\-|]*([\d]{1,2}(?:\.\d+)?)\s*(?:mg/?dL|mg/dl)?",
    "Sodium":                  r"(?i)(sodium|Na\+?)\b[\s:=\-|]*([\d]{2,3}(?:\.\d+)?)\s*(?:mEq/?L|mmol/?L)?",
    "Potassium":               r"(?i)(potassium|K\+?)\b[\s:=\-|]*([\d]{1}(?:\.\d+)?)\s*(?:mEq/?L|mmol/?L)?",
    "Heart Rate / Pulse":      r"(?i)(heart\s+rate|pulse|HR\b|P\.R\.)\b[\s:=\-|]*([\d]{2,3}(?:\.\d+)?)\s*(?:bpm|/min)?",
    "Blood Pressure":          r"(?i)(blood\s+pressure|BP\b)\b[\s:=\-|]*([\d]{2,3}\s*[/\\|I]\s*[\d]{2,3})",
    "Oxygen Saturation (SpO2)":r"(?i)(SpO ?2|oxygen\s+sat(?:uration)?|O2\s+sat)\b[\s:=\-|]*([\d]{2,3}(?:\.\d+)?)\s*%?",
    "Body Temperature":        r"(?i)(body\s+temp(?:erature)?|temperature|temp\.?)\b[\s:=\-|]*([\d]{2}(?:\.\d+)?)\s*(?:°C|C|°F|F)?",
}


def _preprocess_image(img: "Image.Image") -> "Image.Image":
    """Enhance image for better OCR accuracy — scale up, sharpen, increase contrast."""
    # Scale ×2 using LANCZOS
    w, h = img.size
    img = img.resize((w * 2, h * 2), Image.LANCZOS)
    # Convert to grayscale
    img = img.convert("L")
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.SHARPEN)
    # Enhance contrast
    img = ImageEnhance.Contrast(img).enhance(2.0)
    return img


def _extract_text_from_image(file_obj) -> tuple[str, str | None]:
    """Run Tesseract OCR with pre-processing."""
    if not OCR_SUPPORTED:
        return "", "pytesseract / Pillow not installed."
    tess_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tess_path):
        pytesseract.pytesseract.tesseract_cmd = tess_path
    try:
        raw_img = Image.open(io.BytesIO(file_obj.getvalue()))
        processed = _preprocess_image(raw_img)
        # Run with English PSM 6 (assume a single uniform block of text)
        custom_config = r"--oem 3 --psm 6"
        text = pytesseract.image_to_string(processed, config=custom_config)
        return text, None
    except pytesseract.pytesseract.TesseractNotFoundError:
        return "", ("Tesseract OCR is not installed. "
                    "Download it from https://github.com/UB-Mannheim/tesseract/wiki "
                    "and install to C:\\Program Files\\Tesseract-OCR\\.")
    except Exception as e:
        return "", f"Image processing error: {e}"


def _clean_numeric(raw: str) -> float | None:
    """Strip commas/spaces and convert to float. Returns None on failure."""
    try:
        return float(raw.replace(",", "").replace(" ", ""))
    except (ValueError, AttributeError):
        return None


def _normalize_bp(value: str) -> str:
    """Normalise blood pressure string — fix I → / artefacts."""
    return re.sub(r"[|I]", "/", value).replace(" ", "")


def _interpret_single(key: str, raw_value: str) -> dict:
    """Return a dict with value, unit, status, and clinical message."""
    ref = NORMAL_RANGES.get(key)

    # Blood pressure is special — not a simple single float
    if key == "Blood Pressure":
        normalised = _normalize_bp(raw_value)
        parts = re.split(r"[/]", normalised)
        if len(parts) == 2:
            try:
                systolic, diastolic = float(parts[0]), float(parts[1])
                if systolic >= 180 or diastolic >= 120:
                    status, msg = "Critical", "Hypertensive Crisis — seek emergency medical care."
                elif systolic >= 140 or diastolic >= 90:
                    status, msg = "High", "Stage 2 Hypertension — consult a cardiologist promptly."
                elif systolic >= 130 or diastolic >= 80:
                    status, msg = "Elevated", "Stage 1 Hypertension — lifestyle changes recommended."
                elif systolic < 90 or diastolic < 60:
                    status, msg = "Low", "Hypotension — ensure adequate hydration and monitor."
                else:
                    status, msg = "Normal", "Blood pressure is within the healthy optimal range."
                return {"value": normalised, "unit": "mmHg", "status": status, "message": msg}
            except ValueError:
                pass
        return {"value": normalised, "unit": "mmHg", "status": "Recorded", "message": "Manual clinical review advised."}

    if ref is None:
        return {"value": raw_value, "unit": "", "status": "Recorded", "message": "No reference range available."}

    numeric = _clean_numeric(raw_value)
    unit = ref.get("unit", "")

    if numeric is None:
        return {"value": raw_value, "unit": unit, "status": "Recorded", "message": "Could not parse numeric value."}

    # Normalise WBC / Platelets that may be in absolute cell count
    scale = ref.get("scale_threshold")
    if scale and numeric > scale:
        numeric = round(numeric / 1000.0, 2)

    lo, hi = ref.get("default", (None, None))
    low_msg = ref.get("low_msg")
    high_msg = ref.get("high_msg")

    if lo is not None and numeric < lo:
        status = "Low"
        msg = low_msg or f"Below normal range ({lo}–{hi} {unit})."
    elif hi is not None and numeric > hi:
        status = "High"
        msg = high_msg or f"Above normal range ({lo}–{hi} {unit})."
    else:
        status = "Normal"
        msg = f"Within the healthy reference range ({lo}–{hi} {unit})."

    display_val = str(numeric) if scale else raw_value.strip()
    return {"value": f"{display_val} {unit}".strip(), "unit": unit, "status": status, "message": msg}


def parse_report(file_obj) -> tuple[dict, str | None]:
    """
    Parse a medical report (PDF, TXT, or Image) and return structured metrics
    with clinical interpretation for every detected biomarker.
    """
    text = ""

    try:
        fname = file_obj.name.lower()

        if fname.endswith(".pdf"):
            if not PDF_SUPPORTED:
                return None, "PyPDF2 not installed — PDF parsing unavailable."
            reader = PyPDF2.PdfReader(file_obj)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"

        elif fname.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
            text, err = _extract_text_from_image(file_obj)
            if err:
                return None, err

        else:
            # Plain text / CSV etc.
            try:
                text = file_obj.getvalue().decode("utf-8", errors="ignore")
            except Exception:
                text = file_obj.read().decode("utf-8", errors="ignore")

    except Exception as e:
        return None, f"Error reading document: {e}"

    if not text.strip():
        return None, ("Document appears empty, encrypted, or too low quality for OCR. "
                      "Please upload a higher-resolution scan.")

    # ── Run all extraction patterns ──────────────────────────────────────────
    raw_extractions = {}
    for key, pattern in EXTRACT_PATTERNS.items():
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if m:
            raw_extractions[key] = m.group(2).strip()

    # ── Interpret each extracted value ───────────────────────────────────────
    interpreted = {}
    for key, raw_val in raw_extractions.items():
        interpreted[key] = _interpret_single(key, raw_val)

    # ── Fallback: return meaningful raw lines if nothing structured found ────
    fallback_lines = []
    if not interpreted:
        keywords = [
            "hemoglobin", "wbc", "rbc", "platelet", "glucose", "sugar",
            "cholesterol", "creatinine", "urea", "bun", "sodium", "potassium",
            "bp", "blood pressure", "heart rate", "pulse", "esr", "pcv",
            "hematocrit", "spo2", "temperature", "hb", "ldl", "hdl", "uric"
        ]
        for line in text.split("\n"):
            if any(kw in line.lower() for kw in keywords):
                clean = line.strip()
                if 5 < len(clean) < 80:
                    fallback_lines.append(clean)

    return {
        "raw_text": text,
        "metrics": interpreted,
        "fallback_lines": fallback_lines[:10],
    }, None
