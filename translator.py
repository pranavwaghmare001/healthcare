from deep_translator import GoogleTranslator

def translate_text(text, target_lang="en"):
    """
    Translates text to target language.
    """
    if target_lang == "en" or not text:
        return text
    try:
        # Split text into manageable chunks if needed (Google API limit ~5k chars)
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        print(f"Translation Error: {e}")
        return text # fallback to original

def get_supported_languages():
    return {
        "English": "en", 
        "Hindi (\u0939\u093f\u0902\u0926\u0940)": "hi", 
        "Spanish (Espa\u00f1ol)": "es", 
        "French (Fran\u00e7ais)": "fr",
        "German (Deutsch)": "de"
    }
