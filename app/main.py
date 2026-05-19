import os
import shutil
import requests
from fastapi import FastAPI, UploadFile, Form, HTTPException, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

load_dotenv()

EXTERNAL_BACKEND_URL = os.getenv("EXTERNAL_BACKEND_URL", "")

from app.extractor import extract_text, generate_uk_restaurant_prompt
from app.vapi_client import create_assistant, link_telephony

app = FastAPI(title="Vapi AI Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)

class TelephonyLinkRequest(BaseModel):
    assistant_id: str
    twilio_number: str
    manager_number: str

@app.post("/api/agents/create")
async def create_agent(
    business_id: str = Form(...),
    rules_file: UploadFile = File(...),
    menu_file: UploadFile = File(...)
):
    """
    1. Receives the Business Rules (PDF/Doc) and Menu (Excel/CSV)
    2. Extracts the text using extractor.py
    3. Merges them into a highly optimized UK Restaurant System Prompt
    4. Calls Vapi to provision the agent, injecting the business_id as metadata.
    """
    try:
        # Save files temporarily
        rules_path = f"uploads/{business_id}_rules_{rules_file.filename}"
        menu_path = f"uploads/{business_id}_menu_{menu_file.filename}"
        
        with open(rules_path, "wb") as buffer:
            shutil.copyfileobj(rules_file.file, buffer)
            
        with open(menu_path, "wb") as buffer:
            shutil.copyfileobj(menu_file.file, buffer)
            
        # Extract Text
        rules_text = extract_text(rules_path)
        menu_text = extract_text(menu_path)
        
        # Generate Perfect Prompt
        system_prompt = generate_uk_restaurant_prompt(rules_text, menu_text)
        
        # Create Vapi Assistant (Auto-links the global tool ID from .env)
        vapi_response = create_assistant(business_id, system_prompt)
        
        # Clean up files
        os.remove(rules_path)
        os.remove(menu_path)
        
        return {
            "status": "success",
            "business_id": business_id,
            "assistant_id": vapi_response.get("id"),
            "vapi_response": vapi_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/telephony/link")
async def link_phone(request: TelephonyLinkRequest):
    """
    Links a Twilio phone number to a specific Vapi assistant.
    Also records the manager_number (can be used for call transfers later).
    """
    try:
        response = link_telephony(
            assistant_id=request.assistant_id,
            twilio_number=request.twilio_number,
            manager_number=request.manager_number
        )
        
        return {
            "status": "success",
            "message": "Telephony linked successfully.",
            "vapi_response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- VAPI WEBHOOKS (MOVED FROM MOCK BACKEND) ---

@app.post("/webhook/order")
async def handle_order(request: Request):
    """Receives the LIVE ORDER tool call from Vapi"""
    body = await request.body()
    if not body:
        return {"status": "error", "message": "Empty request body"}
    
    data = await request.json()
    
    # DEBUG: Print raw data to see exactly what Vapi sends
    print(f"DEBUG ORDER DATA: {data}")

    # For apiRequest tools, Vapi sends the arguments directly in the root or inside 'message'
    if "customer_name" in data:
        # This is a flat apiRequest tool call
        args = data
        business_id = "Dashboard Tool"
        print(f"\n--- 🍕 NEW ORDER RECEIVED for {business_id} ---")
        print(f"Customer: {args.get('customer_name')}")
        print(f"Email: {args.get('customer_email')}")
        print(f"Items: {args.get('order_items')}")
        print(f"Total: £{args.get('total_price')}")
        print("-------------------------------------------\n")

        # --- FORWARD TO EXTERNAL BACKEND ---
        if EXTERNAL_BACKEND_URL:
            try:
                forward_payload = {
                    "business_id": business_id,
                    "customer_name": args.get("customer_name"),
                    "customer_email": args.get("customer_email"),
                    "order_items": args.get("order_items"),
                    "total_price": args.get("total_price"),
                    "source": "vapi_voice_agent"
                }
                requests.post(EXTERNAL_BACKEND_URL, json=forward_payload, timeout=5)
                print(f"✅ Order forwarded to {EXTERNAL_BACKEND_URL}")
            except Exception as e:
                print(f"❌ Failed to forward order: {str(e)}")

        return {"status": "success", "message": "Order saved"}

    else:
        # This is a Vapi Server tool call
        message = data.get("message", {})
        tool_calls = message.get("toolCalls", [])
        
        results = []
        for tool_call in tool_calls:
            args = tool_call.get("function", {}).get("arguments", {})
            business_id = message.get("customer", {}).get("metadata", {}).get("business_id", "Unknown")

            print(f"\n--- 🍕 NEW ORDER RECEIVED for {business_id} ---")
            print(f"Customer: {args.get('customer_name')}")
            print(f"Email: {args.get('customer_email')}")
            print(f"Items: {args.get('order_items')}")
            print(f"Total: £{args.get('total_price')}")
            print("-------------------------------------------\n")

            # --- FORWARD TO EXTERNAL BACKEND ---
            if EXTERNAL_BACKEND_URL:
                try:
                    forward_payload = {
                        "business_id": business_id,
                        "customer_name": args.get("customer_name"),
                        "customer_email": args.get("customer_email"),
                        "order_items": args.get("order_items"),
                        "total_price": args.get("total_price"),
                        "source": "vapi_voice_agent"
                    }
                    requests.post(EXTERNAL_BACKEND_URL, json=forward_payload, timeout=5)
                    print(f"✅ Order forwarded to {EXTERNAL_BACKEND_URL}")
                except Exception as e:
                    print(f"❌ Failed to forward order: {str(e)}")

            results.append({
                "toolCallId": tool_call.get("id"),
                "result": "Order saved successfully"
            })
            
        return {"results": results}

@app.post("/webhook/summary")
async def handle_summary(request: Request):
    """Receives the POST-CALL summary from Vapi"""
    data = await request.json()
    
    message = data.get("message", {})
    msg_type = data.get("type") or message.get("type")
    
    # Only process 'end-of-call-report' or 'status-update' that actually has a summary
    call_data = message.get("call", data.get("call", {}))
    analysis = call_data.get("analysis", {})
    summary = analysis.get("summary")

    if not summary:
        return {"status": "ignored", "reason": "no summary in this packet"}

    business_id = call_data.get("metadata", {}).get("business_id", "Unknown")

    print(f"\n--- 📝 FINAL CALL SUMMARY for {business_id} ---")
    print(f"AI Summary: {summary}")
    print(f"Transcript Snippet: {call_data.get('transcript', '')[:100]}...")
    print("------------------------------------------\n")

    return {"status": "received"}


@app.post("/api/webhook/vapi")
async def vapi_tool_fallback(request: Request):
    """Fallback for when the dashboard tool URL is set to /api/webhook/vapi"""
    return await handle_order(request)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
