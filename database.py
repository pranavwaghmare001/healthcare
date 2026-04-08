import sqlite3
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import os

DB_NAME = "smart_health.db"
FIREBASE_CONFIGURED = False

def init_db():
    global FIREBASE_CONFIGURED
    # 1. SQLite Edge-Database (Lightning fast Authentication Layer)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Safe alteration for existing hackathon databases
    try:
        c.execute("ALTER TABLE users ADD COLUMN full_name TEXT;")
    except: pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN age INTEGER;")
    except: pass
    
    conn.commit()
    conn.close()
    
    # 2. Google Cloud Firestore Database (Persistent Medical Cloud Sync)
    cert_path = "firebase_admin_key.json"
    if os.path.exists(cert_path):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(cert_path)
                firebase_admin.initialize_app(cred)
            FIREBASE_CONFIGURED = True
            print("[INFO] Successfully linked Google Cloud Firestore capability!")
        except Exception as e:
            print(f"Firebase Init Error: {e}")

def save_history(user_id, record_type, data):
    """
    Saves a predictive scan or OCR report to the authenticated user's DB profile.
    Pushes directly to Google Cloud Firestore if connected.
    """
    if not user_id or user_id == -1:
        return
        
    if FIREBASE_CONFIGURED:
        try:
            db = firestore.client()
            doc_ref = db.collection('medical_history').document()
            doc_ref.set({
                'user_id': str(user_id),
                'record_type': record_type,
                'data_json': json.dumps(data),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Firestore Sync Error: {e}")

def get_history(user_id):
    """
    Retrieves the entire chronological medical timeline from Google Cloud.
    """
    if not user_id or user_id == -1: return []
    
    results = []
    if FIREBASE_CONFIGURED:
        try:
            db = firestore.client()
            # Fetching all records for the user without order_by bypasses complex composite index requirements
            docs = db.collection('medical_history').where(
                filter=firestore.FieldFilter('user_id', '==', str(user_id))
            ).stream()
            
            for doc in docs:
                d = doc.to_dict()
                time_str = d.get('timestamp', "Unknown Time")
                # Format to a nicer string if it was isoformat
                if "T" in time_str:
                    try:
                        dt = datetime.fromisoformat(time_str)
                        time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except: pass
                    
                results.append({
                    "type": d.get('record_type'),
                    "data": json.loads(d.get('data_json', '{}')),
                    "time": time_str,
                    "raw_time": d.get('timestamp', "")
                })
                
            # Sort explicitly in python chronologically
            results.sort(key=lambda x: x['raw_time'], reverse=True)
            
        except Exception as e:
            print(f"Firestore Fetch Error: {e}")
            
    return results
