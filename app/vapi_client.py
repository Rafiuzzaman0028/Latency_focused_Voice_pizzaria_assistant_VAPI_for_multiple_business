import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY", "your-vapi-api-key")
VAPI_BASE_URL = "https://api.vapi.ai"
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

HEADERS = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json"
}

def create_assistant(business_id: str, system_prompt: str) -> dict:
    """
    Creates an assistant on Vapi and injects the business_id as metadata.
    Also defines an analysisPlan to automatically extract the order summary.
    """
    url = f"{VAPI_BASE_URL}/assistant"
    
    payload = {
        "name": business_id,
        "firstMessage": "Hello! How can I help you today?",
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
            "temperature": 0.4
        },
        "voice": {
            "provider": "11labs",
            "voiceId": "JBFqnCBsd6RMkjVDRZzb", # George (British) voice ID
            "model": "eleven_flash_v2_5" # Fast ElevenLabs model for minimum latency
        },
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en-GB"
        },
        # Instruct Vapi to extract the order structure and generate a summary post-call
        "analysisPlan": {
            "summaryPrompt": "Summarize the call focusing on the customer's intent and any issues.",
            "structuredDataPrompt": "Extract the items the customer ordered and their quantities.",
            "structuredDataSchema": {
                "type": "object",
                "properties": {
                    "order_items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_name": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "notes": {"type": "string"}
                            }
                        }
                    },
                    "delivery_or_collection": {"type": "string", "enum": ["delivery", "collection"]},
                    "customer_postcode": {"type": "string"}
                }
            }
        }
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    
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
