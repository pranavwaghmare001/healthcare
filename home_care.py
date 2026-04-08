
# Dictionary containing lifestyle tips.
# We map known diseases to specific tips, and provide a comprehensive default.

HOME_CARE_MAP = {
    "Allergy": {
        "diet": "Avoid known trigger foods. Eat local honey and anti-inflammatory foods like berries.",
        "hydration": "Drink warm water with lemon to soothe your throat.",
        "rest": "Stay indoors when pollen counts are high. Keep windows closed.",
        "remedies": "Take a steamy shower to clear nasal passages."
    },
    "GERD": {
        "diet": "Avoid spicy, acidic, and fatty foods. Eat smaller, more frequent meals.",
        "hydration": "Drink water between meals rather than during them.",
        "rest": "Do not lie down immediately after eating. Elevate the head of your bed.",
        "remedies": "Chew non-mint gum to increase saliva production."
    },
    "Malaria": {
        "diet": "Eat light, easily digestible foods like porridge, soup, and boiled vegetables.",
        "hydration": "Drink plenty of electrolytes and fresh juices to prevent dehydration from fever.",
        "rest": "Complete bed rest is absolutely necessary.",
        "remedies": "Use mosquito nets and repellents to prevent further bites while recovering."
    },
    "Migraine": {
        "diet": "Avoid caffeine withdrawal, aged cheeses, and artificial sweeteners.",
        "hydration": "Maintain consistent hydration; dehydration is a major migraine trigger.",
        "rest": "Rest in a quiet, completely dark room.",
        "remedies": "Apply a cold compress or ice pack to your forehead."
    },
    "Common Cold": {
        "diet": "Eat warm foods like chicken soup to relieve congestion.",
        "hydration": "Drink plenty of warm herbal teas and water.",
        "rest": "Take frequent naps and prioritize sleeping at least 8 hours.",
        "remedies": "Use a saline nasal spray or gargle with warm salt water."
    },
    "default": {
        "diet": "Eat a balanced, nutritious diet rich in vitamins to support your immune system.",
        "hydration": "Drink at least 8 glasses of water daily to stay properly hydrated.",
        "rest": "Get plenty of rest (7-9 hours of sleep) to aid your body's recovery.",
        "remedies": "Avoid strenuous activities and stress until you feel completely better."
    }
}

def get_home_care(disease, severity, age):
    care = HOME_CARE_MAP.get(disease, HOME_CARE_MAP["default"])
    
    tips = {
        "diet": "🍽️ **Diet Advice:** " + care["diet"],
        "hydration": "💧 **Hydration Tips:** " + care["hydration"],
        "rest": "🛏️ **Rest & Recovery:** " + care["rest"],
        "remedies": "🌿 **Home Remedies:** " + care["remedies"]
    }
    
    # Safely handle 'Unknown' severity
    if severity == "Unknown":
        severity = "Medium" # Fallback heuristic
        
    if severity == "High":
        tips["warning"] = "⚠️ **SEVERE CONDITION WARNING:** You are showing signs of a potentially severe condition. These lifestyle tips DO NOT replace medical treatment. Please consult a doctor immediately."
        
    if age:
        if age > 65:
            tips["age_note"] = "👴👵 **Age Context:** As an older adult (65+), your immune response may need more support. Monitor your symptoms closely and do not hesitate to contact a doctor."
        elif age < 12:
            tips["age_note"] = "👶 **Age Context:** For young children, illnesses can escalate quickly. Ensure constant adult supervision and maintain hydration."
            
    return tips
