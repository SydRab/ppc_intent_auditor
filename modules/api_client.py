import os
import json
from google import genai
from google.genai import types
from config.rules import MARKETCALL_OFFER_RULES

def get_gemini_client():
    """Initializes and returns the Gemini API client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")
    return genai.Client(api_key=api_key)

def evaluate_keyword_batch(client: genai.Client, keywords_batch: list) -> list:
    """Sends a single batch of keywords to Gemini 2.5 Flash for compliance filtering."""
    prompt = f"""
    You are an expert PPC campaign manager and affiliate compliance auditor. 
    Review the following list of keywords against the strict MarketCall offer rules below.
    
    {MARKETCALL_OFFER_RULES}
    
    INSTRUCTIONS:
    1. EXCLUDE any keyword containing competitor brand names, prohibited pests, DIY/informational intent, or building type violations.
    2. KEEP high-intent commercial or emergency local service terms strictly matching accepted household pests.
    3. ASSIGN a logical Google Ads "ad_group" category name for approved keywords.
    
    KEYWORDS:
    {json.dumps(keywords_batch)}
    
    Return response strictly as a JSON list of objects:
    [
      {{"keyword": "example", "status": "KEEP", "reason": "valid intent", "ad_group": "Termite Exterminator"}},
      {{"keyword": "bad", "status": "EXCLUDE", "reason": "prohibited pest", "ad_group": "N/A"}}
    ]
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        return []
