import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY", "your-vapi-api-key")
VAPI_BASE_URL = "https://api.vapi.ai"
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
VAPI_DEFAULT_TOOL_ID = os.getenv("VAPI_DEFAULT_TOOL_ID", "")
VAPI_SERVER_URL = os.getenv("VAPI_SERVER_URL", "")

HEADERS = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json"
}

def create_assistant(business_id: str, system_prompt: str) -> dict:
    """
    Creates an assistant on Vapi and automatically attaches the pre-configured
    Order Tool ID from the environment.
    """
    url = f"{VAPI_BASE_URL}/assistant"
    
    # Strictly use the tool ID configured in the .env for all agents
    tool_ids = []
    if VAPI_DEFAULT_TOOL_ID:
        tool_ids.append(VAPI_DEFAULT_TOOL_ID)

    payload = {
        "name": business_id, # Exactly the name you provide
        "firstMessage": "Hello! Thanks for calling. How can I help you with your order today?",
        "serverUrl": VAPI_SERVER_URL, # Auto-links the summary webhook from .env
        "metadata": {
            "business_id": business_id
        },
        "model": {
            "provider": "openai",
            "model": LLM_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ],
            "temperature": 0.4,
            "toolIds": tool_ids # Links your dashboard-created tool
        },
        "voice": {
            "provider": "11labs",
            "voiceId": "JBFqnCBsd6RMkjVDRZzb",
            "model": "eleven_flash_v2_5"
        },
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en-GB"
        },
        "analysisPlan": {
            "summaryPrompt": "Provide a concise summary of the call. Include the customer's name, their mood, what they ordered, and if the order was successfully handled.",
            "structuredDataPrompt": "Extract the final order details for database logging.",
            "structuredDataSchema": {
                "type": "object",
                "properties": {
                    "final_items": {"type": "array", "items": {"type": "string"}},
                    "total_paid": {"type": "number"},
                    "order_status": {"type": "string", "enum": ["completed", "abandoned", "in_progress"]}
                }
            }
        }
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code >= 400:
        # Return the actual error from Vapi so it shows in the browser
        error_msg = response.text
        raise Exception(f"Vapi Error: {error_msg}")
    
    return response.json()


def link_telephony(assistant_id: str, twilio_number: str, manager_number: str) -> dict:
    """
    Links a Twilio phone number to the created Vapi assistant.
    The twilio_number must exist in the Twilio account linked to Vapi.
    """
    url = f"{VAPI_BASE_URL}/phone-number"
    
    payload = {
        "provider": "twilio",
        "number": twilio_number,
        "assistantId": assistant_id,
        "twilioAccountSid": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "twilioAuthToken": os.getenv("TWILIO_AUTH_TOKEN", ""),
        "name": f"Line for {assistant_id}"
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    
    return response.json()
