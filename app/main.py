import os
import shutil
from fastapi import FastAPI, UploadFile, Form, HTTPException, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

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
        
        # Create Vapi Assistant
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


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
