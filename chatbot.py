def get_bot_response(user_input, symptoms_list):
    """
    Rule-based chatbot engine returning dynamic responses based on input.
    """
    user_input = user_input.lower()
    
    greetings = ["hi ", "hello", "hey", "help", "start"]
    if any(g in user_input for g in greetings) or user_input in ["hi", "hey"]:
        return "Hello! 👋 I am your AI Health Assistant. You can use the Diagnosis tab above for symptom checking, or ask me for general info about diseases."
        
    symptom_inquiry = ["symptom", "pain", "feeling", "sick", "ill", "fever", "hurt"]
    if any(s in user_input for s in symptom_inquiry):
        return "It sounds like you're experiencing some distress. Please navigate to the **Diagnosis & Emergency** tab. Entering your complete symptoms there will give me the best data to help you safely."
        
    emergency = ["chest pain", "faint", "can't breathe", "ambulance"]
    if any(e in user_input for e in emergency):
        return "🚨 **EMERGENCY WARNING**: If you are experiencing critical symptoms like chest pain or breathing issues, PLEASE CALL 108 or your local emergency number IMMEDIATELY."
        
    # Check if a known exact symptom from the database is mentioned
    mentioned_symptoms = [s for s in symptoms_list if s.lower() in user_input]
    if mentioned_symptoms:
        return f"I noticed you mentioned these specific symptoms: **{', '.join(mentioned_symptoms)}**. I strongly advise running a full Diagnosis on the main tab to safely assess probabilities."
        
    return "I am a streamlined medical AI prototype. To best assist you, try searching for a custom disease on the 'Lookup' tab or run a full diagnosis mapping!"
