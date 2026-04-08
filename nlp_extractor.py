import re

class SymptomExtractor:
    def __init__(self, known_symptoms):
        """
        Initialize the extractor with a list or set of known symptoms.
        Convert to lowercase for case-insensitive matching.
        """
        self.known_symptoms = [s.lower() for s in known_symptoms]
        
    def extract_symptoms(self, text):
        """
        Simple keyword-based NLP approach.
        In a hackathon setting, a brute-force n-gram match or simple presence check works great.
        """
        if not text or not isinstance(text, str):
            return []
            
        text = text.lower()
        # Basic preprocessing: remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        
        extracted = []
        for symptom in self.known_symptoms:
            # Simple substring checking. Use word boundaries to avoid partial matches
            # e.g., 'ache' matching inside 'headache', though 'headache' is a distinct symptom
            # For multi-word symptoms like "shortness of breath", direct string matching is better.
            
            # Use regex to match whole words or exact phrases
            pattern = r'\b' + re.escape(symptom) + r'\b'
            if re.search(pattern, text):
                extracted.append(symptom)
                
            # Alternative: Fallback for complex ones
            elif symptom in text:
                if symptom not in extracted:
                    extracted.append(symptom)
                    
        # Map common human synonyms to Kaggle dataset vectors
        synonyms = {
            "dull": ["lethargy", "fatigue"],
            "tired": ["fatigue"],
            "exhausted": ["fatigue"],
            "hurt": ["pain", "muscle_pain"],
            "hot": ["fever", "high_fever"],
            "cold": ["chills"],
            "puking": ["vomiting"],
            "throw up": ["vomiting"],
            "belly": ["stomach_pain"],
            "dizzy": ["dizziness"],
            "runny nose": ["continuous_sneezing"]
        }
        
        for k, v_list in synonyms.items():
            if re.search(r'\b' + k + r'\b', text):
                for v in v_list:
                    if v in self.known_symptoms and v not in extracted:
                        extracted.append(v)
                    
        return list(set(extracted))

if __name__ == "__main__":
    # Quick test
    sample_symptoms = ["headache", "fever", "shortness of breath", "chest pain"]
    extractor = SymptomExtractor(sample_symptoms)
    test_text = "I have a severe headache and I've been running a fever since yesterday. I also have shortness of breath."
    print("Extracted:", extractor.extract_symptoms(test_text))
