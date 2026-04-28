# import os
# from fastapi import FastAPI, UploadFile, File, Request
# from dotenv import load_dotenv
# from pydantic import BaseModel

# from app.extractor import extract_text
# from app.report_generator import generate_ai_report
# from app.script_generator import generate_voice_script
# from app.rag_answer import generate_answer
# from fastapi.responses import Response
# from twilio.twiml.voice_response import VoiceResponse

# from app.voice_webhook import voice_entry, voice_process
# from app.transcript_store import get_transcript, clear_call
# from app.call_logger import save_call_log
# from app.call_summary import generate_summary

# load_dotenv()

# app = FastAPI()


# # ------------------ UPLOAD DOC ------------------

# @app.post("/upload-doc/")
# async def upload_doc(file: UploadFile = File(...)):
#     os.makedirs("uploads", exist_ok=True)
#     os.makedirs("reports", exist_ok=True)

#     file_path = f"uploads/{file.filename}"

#     with open(file_path, "wb") as f:
#         f.write(await file.read())

#     raw_text = extract_text(file_path)

#     # Generate report
#     report = generate_ai_report(raw_text)

#     # Generate script
#     script = generate_voice_script(report)

#     # Save versioned (optional history)
#     with open(f"reports/{file.filename}_report.txt", "w", encoding="utf-8") as f:
#         f.write(report)

#     with open(f"reports/{file.filename}_script.txt", "w", encoding="utf-8") as f:
#         f.write(script)

#     # Save CURRENT (used by voice + ask)
#     with open("reports/current_report.txt", "w", encoding="utf-8") as f:
#         f.write(report)

#     with open("reports/current_script.txt", "w", encoding="utf-8") as f:
#         f.write(script)

#     return {"message": "Report and Script updated for current system"}


# # ------------------ ASK (RAG) ------------------

# class Question(BaseModel):
#     question: str


# @app.post("/ask/")
# async def ask_question(data: Question):
#     answer = generate_answer(
#         data.question,
#         "reports/current_report.txt",
#         "reports/current_script.txt"
#     )
#     return {"answer": answer}


# # ------------------ VOICE ------------------

# @app.post("/voice")
# async def voice(request: Request):
#     return await voice_entry(request)


# @app.post("/voice-process")
# async def voice_process_route(request: Request):
#     return await voice_process(request)


# # ------------------ CALL END (save logs + summary) ------------------

# @app.post("/call-end")
# async def call_end(request: Request):
#     form = await request.form()
#     call_id = form.get("CallSid")

#     transcript = get_transcript(call_id)

#     save_call_log(call_id, transcript)
#     summary = generate_summary(call_id, transcript)

#     clear_call(call_id)

#     return {"status": "saved", "summary": summary}


# # ------------------ LIVE TRANSCRIPT ------------------

# @app.get("/live-transcript/{call_id}")
# async def live_transcript(call_id: str):
#     return {"transcript": get_transcript(call_id)}

# # ------------------ TWILIO ENTRY (bypass ngrok warning) ------------------

# @app.api_route("/twilio-entry", methods=["GET", "POST"])
# def twilio_entry():
#     vr = VoiceResponse()
#     vr.redirect("/voice")
#     return Response(content=str(vr), media_type="text/xml")

<<<<<<< HEAD
from fastapi import FastAPI, UploadFile, File, Request, Form
from dotenv import load_dotenv
from pydantic import BaseModel
import os
=======
import os
from fastapi import FastAPI, UploadFile, File, Request
from dotenv import load_dotenv
from pydantic import BaseModel
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f

from app.extractor import extract_text
from app.report_generator import generate_ai_report
from app.script_generator import generate_voice_script
from app.rag_answer import generate_answer
<<<<<<< HEAD
from app.db_mock import save_tenant
=======
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f

# Twilio voice handlers
from app.voice_webhook import voice_entry, voice_process

# Call tracking
<<<<<<< HEAD
from app.transcript_store import get_transcript, clear_call, reset_call_state
from app.call_logger import save_call_log
from app.call_summary import generate_summary
=======
from app.transcript_store import get_transcript, clear_call
from app.call_logger import save_call_log
from app.call_summary import generate_summary
from app.transcript_store import get_transcript, clear_call, reset_call_state
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f

# ------------------ INIT ------------------

load_dotenv()
app = FastAPI()

os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("call_logs", exist_ok=True)


# =====================================================
# DOCUMENT UPLOAD → REPORT → SCRIPT
# =====================================================

@app.post("/upload-doc/")
<<<<<<< HEAD
async def upload_doc(
    file: UploadFile = File(...),
    business_name: str = Form(...),
    twilio_phone_number: str = Form(...),
    manager_phone: str = Form(...)
):
=======
async def upload_doc(file: UploadFile = File(...)):
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f

    file_path = f"uploads/{file.filename}"

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract raw text
    raw_text = extract_text(file_path)

    # Generate AI knowledge report
    report = generate_ai_report(raw_text)

    # Generate voice assistant script
    script = generate_voice_script(report)

<<<<<<< HEAD
    # Save history versions (optional, but good for backups)
=======
    # Save history versions
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
    with open(f"reports/{file.filename}_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    with open(f"reports/{file.filename}_script.txt", "w", encoding="utf-8") as f:
        f.write(script)

<<<<<<< HEAD
    # Save to our multi-tenant DB instead of just `current_report.txt`
    tenant_id = save_tenant(
        twilio_phone_number=twilio_phone_number,
        business_name=business_name,
        manager_phone=manager_phone,
        report_text=report,
        script_text=script
    )

    # For backward compatibility during transition, we can still write to current_report
    # But ideally, we rely entirely on the DB now.
=======
    # Save CURRENT active config
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
    with open("reports/current_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    with open("reports/current_script.txt", "w", encoding="utf-8") as f:
        f.write(script)

<<<<<<< HEAD
    from app.db_mock import get_tenant_by_twilio_number
    tenant_profile = get_tenant_by_twilio_number(twilio_phone_number)

    return {
        "message": "Document processed. AI agent updated.", 
        "tenant_id": tenant_id,
        "tenant_profile": tenant_profile
    }
=======
    return {"message": "Document processed. AI agent updated."}
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f


# =====================================================
# RAG QUESTION ANSWERING
# =====================================================

class Question(BaseModel):
    question: str


# @app.post("/ask/")
# async def ask_question(data: Question):

#     answer = generate_answer(
#         data.question,
#         "reports/current_report.txt",
#         "reports/current_script.txt"
#     )

#     return {"answer": answer}

@app.post("/ask/")
async def ask_question(data: Question):

    result = generate_answer(
        data.question,
        "reports/current_report.txt",
        "reports/current_script.txt",
        "test_call"
    )

    return {"answer": result["speak"]}

# =====================================================
# TWILIO VOICE WEBHOOKS
# =====================================================

@app.post("/voice")
async def voice(request: Request):
    return await voice_entry(request)


@app.post("/voice-process")
async def voice_process_route(request: Request):
    return await voice_process(request)


<<<<<<< HEAD
from app.db_mock import save_tenant, save_db_call_log, get_tenant_by_twilio_number

=======
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
# =====================================================
# CALL END → SAVE LOG + SUMMARY
# =====================================================

@app.post("/call-end")
async def call_end(request: Request):

    form = await request.form()
    call_id = form.get("CallSid")
<<<<<<< HEAD
    to_number = form.get("To", "")
    from_number = form.get("From", "")

    transcript = get_transcript(call_id)

    tenant = get_tenant_by_twilio_number(to_number) or get_tenant_by_twilio_number(from_number)
    caller_phone = from_number if get_tenant_by_twilio_number(to_number) else to_number
    tenant_id = tenant["tenant_id"] if tenant else "unknown_tenant"

    # Save transcript file to DB
    save_db_call_log(tenant_id, caller_phone, call_id, transcript)
=======

    transcript = get_transcript(call_id)

    # Save transcript file
    save_call_log(call_id, transcript)
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f

    # Generate AI summary
    summary = generate_summary(call_id, transcript)

<<<<<<< HEAD
    # Convert transcript string to JSON array format
    transcript_array = []
    for line in transcript.split("\n"):
        if line.startswith("User: "):
            transcript_array.append({"role": "user", "content": line.replace("User: ", "", 1)})
        elif line.startswith("AI: "):
            transcript_array.append({"role": "assistant", "content": line.replace("AI: ", "", 1)})

    # Fetch order (if any)
    from app.db_mock import get_order_by_call_id
    import json
    order = get_order_by_call_id(call_id)
    
    # ALWAYS save the call details, even if no order was placed
    os.makedirs(f"saved_orders/{tenant_id}", exist_ok=True)
    combined_data = {
        "call_id": call_id,
        "tenant_id": tenant_id,
        "caller_phone": caller_phone,
        "order_details": order.get("order_data") if order else None,
        "call_summary": summary,
        "transcript": transcript_array
    }
    with open(f"saved_orders/{tenant_id}/{call_id}_record.json", "w", encoding="utf-8") as f:
        json.dump(combined_data, f, indent=4)

=======
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
    # Clear memory
    clear_call(call_id)
    reset_call_state(call_id)

    return {"status": "saved", "summary": summary}


# LIVE TRANSCRIPT VIEW
@app.get("/live-transcript/{call_id}")
async def live_transcript(call_id: str):
    return {"transcript": get_transcript(call_id)}
<<<<<<< HEAD


# =====================================================
# INDEPENDENT BACKEND API (For your Backend Developer)
# =====================================================

@app.get("/api/orders/{tenant_id}")
async def get_tenant_orders(tenant_id: str):
    """
    Allows an independent backend to fetch all call records 
    (orders, summaries, and transcripts) for a specific business.
    """
    import json
    records = []
    folder_path = f"saved_orders/{tenant_id}"
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                with open(f"{folder_path}/{filename}", "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        records.append(data)
                    except json.JSONDecodeError:
                        continue
    return {"tenant_id": tenant_id, "call_records": records}
=======
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
