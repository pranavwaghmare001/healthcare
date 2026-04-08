import database
import sys

print("Initializing Database and Firebase Link...")
database.init_db()

if not database.FIREBASE_CONFIGURED:
    print("[ERROR] Firebase failed to configure. Check if 'firebase_admin_key.json' is valid and present.")
    sys.exit(1)

print("Attempting to push a test record to Firestore...")
try:
    # user_id '9999' is a test user
    database.save_history(9999, "prediction", {"test": "Firebase Hackathon Sync", "status": "Working!"})
    print("[SUCCESS] Successfully pushed a dummy prediction to Google Cloud Firestore.")
    
    print("Attempting to fetch the test record back...")
    history = database.get_history(9999)
    if history:
        print(f"[SUCCESS] Successfully retrieved {len(history)} records from Firestore!")
        print("Sample Data:", history[0]['data'])
    else:
        print("[WARNING] Pushed record, but retrieved 0 records.")
        
except Exception as e:
    print(f"[ERROR] Exception occurred during Firestore transaction: {e}")
