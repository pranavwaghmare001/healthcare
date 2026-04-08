import os
import json
import tempfile
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import core internal python logic
import database
import auth
from model import DiseaseModel
from nlp_extractor import SymptomExtractor
import data_generator
from emergency import check_emergency, get_mock_hospitals
from home_care import get_home_care
from report_parser import parse_report
from chatbot import get_bot_response

app = FastAPI(title="Smart Health API Foundation")

@app.on_event("startup")
def startup_event():
    print("Initializing Application Boot Sequences...")
    database.init_db()
    
    if not os.path.exists("dataset.csv"):
        df = data_generator.generate_synthetic_data(num_samples=2000)
        df.to_csv("dataset.csv", index=False)
        
    model = DiseaseModel()
    model.load_and_train("dataset.csv")    
    all_symptoms = model.get_all_symptoms()
    extractor = SymptomExtractor(all_symptoms)
    
    app.state.model = model
    app.state.extractor = extractor
    app.state.all_symptoms = all_symptoms

# -----------------
# REST API ROUTES
# -----------------

class LoginReq(BaseModel):
    username: str
    password: str

class SignupReq(BaseModel):
    username: str
    password: str
    full_name: str
    age: int

@app.post("/api/auth/signup")
def signup(req: SignupReq):
    success, val = auth.create_user(req.username, req.password, req.full_name, req.age)
    if success:
        return {"success": True, "user_id": val}
    else:
        raise HTTPException(status_code=400, detail=val)

@app.post("/api/auth/login")
def login(req: LoginReq):
    success, uid, fname = auth.login_user(req.username, req.password)
    if success:
        return {"success": True, "user_id": uid, "full_name": fname}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

class DiagnoseReq(BaseModel):
    user_id: int
    symptoms: List[str]
    age: int
    location: str

@app.post("/api/diagnose")
def diagnose(req: DiagnoseReq):
    if not req.symptoms:
         raise HTTPException(status_code=400, detail="Missing symptoms parameter")
         
    results, _ = app.state.model.predict(req.symptoms)
    if not results:
         return {"success": False, "message": "Unable to determine disease."}
         
    is_emergency, critical_symptoms = check_emergency(req.symptoms)
    if is_emergency:
         results[0]["severity"] = "High"
         
    hospitals = get_mock_hospitals(req.location) if is_emergency else []
    care_tips = get_home_care(results[0]["disease"], results[0]["severity"], req.age)
    
    database.save_history(req.user_id, 'prediction', {
        'symptoms': req.symptoms,
        'top_disease': results[0]['disease'],
        'probability': results[0]['probability'],
        'severity': results[0]['severity']
    })
    
    return {
        "success": True,
        "results": results,
        "is_emergency": is_emergency,
        "critical_symptoms": critical_symptoms,
        "hospitals": hospitals,
        "care_tips": care_tips
    }

class FilterSymptomsReq(BaseModel):
    text: str

@app.post("/api/extract_symptoms")
def extract_symptoms(req: FilterSymptomsReq):
    extracted = app.state.extractor.extract_symptoms(req.text)
    return {"symptoms": extracted}

@app.get("/api/symptoms")
def get_symptoms():
    return {"symptoms": app.state.all_symptoms}

@app.get("/api/history/{user_id}")
def history(user_id: int):
    recs = database.get_history(user_id)
    return {"history": recs}

@app.post("/api/reports/upload")
def upload_report(user_id: int = Form(...), file: UploadFile = File(...)):
    try:
        # We spoof a local tempfile wrapper since parse_report strictly takes a filepath or object block
        ext = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as fp:
            fp.write(file.file.read())
            tmp_name = fp.name
            
        parsed_data, error = parse_report(tmp_name)
        os.remove(tmp_name)
        
        if error:
             return JSONResponse(status_code=400, content={"success": False, "error": error})
             
        metrics = parsed_data.get("metrics", {})
        
        database.save_history(user_id, 'report', {
             'filename': file.filename,
             'metrics': metrics
        })
        
        return {"success": True, "metrics": metrics}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

class ChatReq(BaseModel):
    message: str

@app.post("/api/chat")
def chat(req: ChatReq):
    ans = get_bot_response(req.message, app.state.all_symptoms)
    return {"response": ans}

# -----------------
# MOUNT CLIENT SPA
# -----------------
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
