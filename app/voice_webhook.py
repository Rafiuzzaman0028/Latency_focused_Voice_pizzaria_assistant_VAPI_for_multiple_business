<<<<<<< HEAD
=======
# import os
# import requests
# from fastapi import Request
# from twilio.twiml.voice_response import VoiceResponse
# from fastapi.responses import Response

# from app.transcript_store import add_line
# from dotenv import load_dotenv
# from app.rag_answer import generate_answer

# load_dotenv()

# BASE_URL = os.getenv("BASE_URL")

# REPORT_PATH = "reports/current_report.txt"
# SCRIPT_PATH = "reports/current_script.txt"


# def get_greeting():
#     with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
#         script = f.read()

#     return script.split("GREETING:")[1].split("TONE:")[0].strip()


# async def voice_entry(request: Request):
#     vr = VoiceResponse()

#     greeting_line = get_greeting()
#     vr.say(greeting_line)

#     vr.gather(
#         input="speech",
#         action="/voice-process",
#         speechTimeout="auto"
#     )

#     # return str(vr)
#     return Response(content=str(vr), media_type="text/xml")



# async def voice_process(request: Request):
#     form = await request.form()

#     user_speech = form.get("SpeechResult")
#     call_id = form.get("CallSid")

#     add_line(call_id, "User", user_speech)

#     # Call RAG endpoint
#     # response = requests.post(
#     #     f"{BASE_URL}/ask/",
#     #     json={"question": user_speech}
#     # )

#     # ai_answer = response.json().get("answer")
#     ai_answer = generate_answer(
#         user_speech,
#         "reports/current_report.txt",
#         "reports/current_script.txt"
#     )


#     add_line(call_id, "AI", ai_answer)

#     vr = VoiceResponse()
#     vr.say(ai_answer)

#     vr.gather(
#         input="speech",
#         action="/voice-process",
#         speechTimeout="auto"
#     )

#     # return str(vr)
#     return Response(content=str(vr), media_type="text/xml")


>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
import os
from fastapi import Request
from twilio.twiml.voice_response import VoiceResponse
from fastapi.responses import Response

from app.transcript_store import add_line
from app.rag_answer import generate_answer

#for error log
import traceback
from fastapi import Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse


<<<<<<< HEAD
from app.db_mock import get_tenant_by_twilio_number, insert_order

def get_greeting_from_script(script_text: str):
    if not script_text:
        return "Hello, how can I help you today?"
    try:
        return script_text.split("GREETING:")[1].split("TONE:")[0].strip()
    except Exception:
        return "Hello, how can I help you today?"


# ENTRY 

async def voice_entry(request: Request):
    vr = VoiceResponse()

    try:
        form = await request.form()
        # For inbound calls, "To" is the Twilio number. For outbound tests, "From" is the Twilio number.
        to_number = form.get("To", "")
        from_number = form.get("From", "")
        
        tenant = get_tenant_by_twilio_number(to_number) or get_tenant_by_twilio_number(from_number)
        
        if tenant:
            greeting_line = get_greeting_from_script(tenant["script_text"])
        else:
            greeting_line = "Welcome! I am unable to locate the business profile for this number."
            
        gather = vr.gather(
            input="speech",
            action="/voice-process",
            speechTimeout="1",
            bargeIn=True,
            profiling="true"
        )
        gather.say(greeting_line)
=======
REPORT_PATH = "reports/current_report.txt"
SCRIPT_PATH = "reports/current_script.txt"


def get_greeting():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        script = f.read()

    return script.split("GREETING:")[1].split("TONE:")[0].strip()


# -------------------- ENTRY --------------------

async def voice_entry(request: Request):

    vr = VoiceResponse()

    try:
        greeting_line = get_greeting()
        vr.say(greeting_line)
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f

    except Exception as e:
        print("\n=== VOICE ENTRY ERROR ===")
        traceback.print_exc()
        vr.say("System initialization error.")

<<<<<<< HEAD
=======
    vr.gather(
        input="speech",
        action="/voice-process",
        speechTimeout="auto"
    )

>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
    return Response(content=str(vr), media_type="text/xml")



<<<<<<< HEAD
=======
# -------------------- PROCESS --------------------

# async def voice_process(request: Request):
#     form = await request.form()

#     user_speech = form.get("SpeechResult", "").strip()
#     call_id = form.get("CallSid")

#     vr = VoiceResponse()

#     # If user said nothing (silence / noise / timeout)
#     if not user_speech:
#         vr.say("I did not catch that. Could you please repeat?")
#         vr.gather(
#             input="speech",
#             action="/voice-process",
#             speechTimeout="auto"
#         )
#         return Response(content=str(vr), media_type="text/xml")

#     # Save user line
#     add_line(call_id, "User", user_speech)

#     # Get AI answer directly from RAG
#     ai_answer = generate_answer(
#         user_speech,
#         REPORT_PATH,
#         SCRIPT_PATH
#     )

#     # Save AI line
#     add_line(call_id, "AI", ai_answer)

#     # Speak answer
#     vr.say(ai_answer)

#     # VERY IMPORTANT — continue the conversation
#     vr.gather(
#         input="speech",
#         action="/voice-process",
#         speechTimeout="auto"
#     )

#     return Response(content=str(vr), media_type="text/xml")


>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
async def voice_process(request: Request):

    vr = VoiceResponse()

    try:
        form = await request.form()

        print("\n--- Incoming Twilio Form ---")
        print(dict(form))

        user_speech = (form.get("SpeechResult") or "").strip()
        call_id = form.get("CallSid") or "unknown_call"
<<<<<<< HEAD
        to_number = form.get("To", "")
        from_number = form.get("From", "Unknown")
        
        # Determine which number is the Twilio Business number and which is the Caller
        tenant = get_tenant_by_twilio_number(to_number) or get_tenant_by_twilio_number(from_number)
        caller_phone = from_number if get_tenant_by_twilio_number(to_number) else to_number
        twilio_number = to_number if get_tenant_by_twilio_number(to_number) else from_number

        if not tenant:
            vr.say("Business profile not found. Please contact support.")
            return Response(content=str(vr), media_type="text/xml")

        if not user_speech:
            gather = vr.gather(
                input="speech",
                action="/voice-process",
                speechTimeout="1",
                bargeIn=True,
                profiling="true"
            )
            gather.say("I did not catch that. Please repeat.")
            return Response(content=str(vr), media_type="text/xml")

        print("User said:", user_speech)
        print("Calling RAG...")

        result = generate_answer(
            user_speech,
            tenant["report_text"],
            tenant["script_text"],
=======

        if not user_speech:
            vr.say("I did not catch that. Please repeat.")
            vr.gather(
                input="speech",
                action="/voice-process",
                speechTimeout="auto"
            )
            return Response(content=str(vr), media_type="text/xml")

        print("User said:", user_speech)

        add_line(call_id, "User", user_speech)

        print("Calling RAG...")

        # ai_answer = generate_answer(
        #     user_speech,
        #     REPORT_PATH,
        #     SCRIPT_PATH
        # )

        # print("AI Answer:", ai_answer)

        # add_line(call_id, "AI", ai_answer)

        # vr.say(ai_answer)

        result = generate_answer(
            user_speech,
            REPORT_PATH,
            SCRIPT_PATH,
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
            call_id
        )

        print("AI Result:", result)

        # Save AI spoken text
        add_line(call_id, "AI", result["speak"])

<<<<<<< HEAD
        # ---- Escalation Handling ----
        if result["intent"] == "escalation":
            vr.say(result["speak"])
            transfer_number = tenant.get("manager_phone", os.getenv("TRANSFER_NUMBER", "+1234567890"))
            
            # Using Twilio number as callerId to ensure it bills correctly & prevents carrier blocking
            if twilio_number:
                vr.dial(transfer_number, caller_id=twilio_number)
            else:
                vr.dial(transfer_number)
                
            return Response(content=str(vr), media_type="text/xml")

        # ---- Order Confirmation Handling ----
        if result.get("order") is not None:
            print("FINAL ORDER JSON:", result["order"])
            # Save to backend database mock
            insert_order(tenant["tenant_id"], caller_phone, call_id, result["order"])
            
        # Speak response WITH Barge-In
        gather = vr.gather(
            input="speech",
            action="/voice-process",
            speechTimeout="1",
            bargeIn=True,
            profiling="true"
        )
        gather.say(result["speak"])
        
=======
        # Speak response
        vr.say(result["speak"])

        # ---- Escalation Handling ----
        if result["intent"] == "escalation":
            # Replace with real number later
            vr.dial("+1234567890")
            return Response(content=str(vr), media_type="text/xml")

        # ---- Order Confirmation Handling ----
        if result["order"] is not None:
            print("FINAL ORDER JSON:", result["order"])
    # Here later you will send to backend API

>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
    except Exception:
        print("\n=== VOICE PROCESS CRASH ===")
        traceback.print_exc()

<<<<<<< HEAD
        gather = vr.gather(
            input="speech",
            action="/voice-process",
            speechTimeout="1",
            bargeIn=True,
            profiling="true"
        )
        gather.say("Sorry, a system error occurred.")
=======
        vr.say("Sorry, a system error occurred.")

    vr.gather(
        input="speech",
        action="/voice-process",
        speechTimeout="auto"
    )
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f

    return Response(content=str(vr), media_type="text/xml")
