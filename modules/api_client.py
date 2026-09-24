import os
import json
from google import genai
from google.genai import types
from config.rules import MARKETCALL_OFFER_RULES

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")
    return genai.Client(api_key=api_key)

def evaluate_keyword_batch(client: genai.Client, keywords_batch: list) -> list:
    prompt = f"""
    You are an expert PPC campaign manager and affiliate compliance auditor. 
    Review the following list of keyword-zip records against the strict MarketCall offer rules below.
    
    {MARKETCALL_OFFER_RULES}
    
    INSTRUCTIONS:
    1. EXCLUDE any record where the keyword contains competitor brand names, prohibited pests (e.g., bed bugs, bees, wildlife), DIY/informational intent ("how to", "home remedies"), or building type violations.
    2. KEEP high-intent commercial or emergency local service terms strictly matching accepted household pests.
    3. ASSIGN a logical Google Ads "ad_group" category name (e.g., "Termite Exterminator", "Ant Control") and a "campaign_name" for approved records.
    
    RECORDS TO REVIEW:
    {json.dumps(keywords_batch)}
    
    Return response strictly as a JSON list of objects matching this exact structure:
    [
      {{
        "keyword": "best ant control",
        "original_zip": "56303",
        "status": "KEEP",
        "reason": "valid commercial intent for accepted pest",
        "campaign_name": "Pest_Control_Search_RTB",
        "ad_group": "Ant Control Near Me"
      }}
    ]
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            ),
        )
        
        # Clean potential markdown code blocks if present
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        return json.loads(raw_text.strip())
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        return []
