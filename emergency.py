import random

def check_emergency(symptoms):
    """
    Checks if any of the provided symptoms classify as a medical emergency.
    Features combination logic, normalization, and standard critical flags.
    """
    # Normalized critical symptoms (lowercase, spaces)
    critical_symptoms = {
        "chest pain", 
        "breathlessness", 
        "shortness of breath", 
        "breathing difficulty",
        "unconsciousness",
        "loss of consciousness",
        "paralysis",
        "altered sensorium",
        "coma",
        "continuous bleeding",
        "acute heart attack",
        "low oxygen",
        "sudden vision loss",
        "severe allergic reaction",
        "seizures"
    }
    
    # Advanced logic: certain combinations are high risk
    high_risk_combos = [
        {"high fever", "stiff neck"},
        {"vomiting", "dizziness", "confusion"}
    ]
    
    # Normalize user symptoms: lowercase and replace underscores with spaces
    norm_user_syms = [s.lower().replace("_", " ").strip() for s in symptoms]
    found_critical = [s for s in norm_user_syms if s in critical_symptoms]
    
    # Special substring checks for flexibility (e.g. "severe chest pain")
    for s in norm_user_syms:
        if any(crit in s for crit in ["chest pain", "shortness of breath", "bleeding"]):
            found_critical.append(s)
    
    # Check combos
    user_syms_set = set(norm_user_syms)
    for combo in high_risk_combos:
        if combo.issubset(user_syms_set):
            found_critical.extend(list(combo))
            
    if found_critical:
        return True, list(set(found_critical))
    return False, []


def get_mock_hospitals(location=""):
    """
    Returns realistic mock hospital data simulated for the given location context.
    """
    location = location.strip().title() if location else "Your Local"
    
    bases = [
        f"{location} General Hospital",
        f"City Care Medical Center ({location})",
        f"Saint Mary's {location} Clinic",
        f"{location} Regional Urgent Care",
        f"Apollo Care {location}"
    ]
    
    # Generate realistic dynamic distances
    hospitals = []
    for name in random.sample(bases, 3):
        dist_val = round(random.uniform(0.5, 8.0), 1)
        time_mins = int(dist_val * 4) + random.randint(-2, 3) # Roughly 4 mins per km
        time_mins = max(time_mins, 2)
        
        status = random.choice(["Available", "Busy", "Available"])
        hospitals.append({
            "name": name,
            "distance": f"{dist_val} km",
            "time": f"{time_mins} mins",
            "status": status,
            "raw_dist": dist_val
        })
        
    # Sort by nearest
    hospitals.sort(key=lambda x: x["raw_dist"])
    return hospitals
