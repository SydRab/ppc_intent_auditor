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
    You are an elite, cutthroat PPC campaign auditor specializing in local-service lead generation and affiliate arbitrage. 
    Evaluate the following list of keyword-zip records against the strict MarketCall offer rules below.
    
    {MARKETCALL_OFFER_RULES}
    
    INSTRUCTIONS FOR CLASSIFICATION:
    1. compliance_status: Classify as "APPROVED" if it's a high-intent commercial or emergency local service term for accepted household pests. Classify as "EXCLUDED" if it violates rules.
    2. intent_type: Classify strictly as "Emergency", "Commercial", "Informational", or "Navigational".
    3. is_phone_intent: Boolean (true/false) indicating if the keyword explicitly signals an immediate desire to call or find a phone number/emergency service.
    4. violation_category: If excluded, choose from ["DIY", "Prohibited_Pest", "Competitor_Brand", "Wrong_Building_Type", "Low_Intent", "None"]. If approved, set to "None".
    5. bid_tier_weight: Assign an integer score: 3 = Emergency phone intent (highest priority), 2 = Standard commercial service intent, 1 = Low priority / long-tail. Set to 0 if excluded.
    6. auto_negative_reason: If excluded, provide a short categorization reason for negative keyword building; otherwise set to "".
    
    RECORDS TO REVIEW:
    {json.dumps(keywords_batch)}
    
    Return response strictly as a JSON list of objects matching this exact structure:
    [
      {{
        "suggested_keyword": "best ant control",
        "original_zip": "56303",
        "compliance_status": "APPROVED",
        "intent_type": "Commercial",
        "is_phone_intent": false,
        "violation_category": "None",
        "bid_tier_weight": 2,
        "auto_negative_reason": ""
      }},
      {{
        "suggested_keyword": "how to get rid of bees naturally",
        "original_zip": "56303",
        "compliance_status": "EXCLUDED",
        "intent_type": "Informational",
        "is_phone_intent": false,
        "violation_category": "DIY",
        "bid_tier_weight": 0,
        "auto_negative_reason": "DIY informational intent and prohibited pest"
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
