import os
from openai import OpenAI
from app.retriever import find_relevant_chunk
from dotenv import load_dotenv
<<<<<<< HEAD
from app.transcript_store import get_call_state, reset_call_state, get_transcript
=======
from app.transcript_store import get_call_state, reset_call_state
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
import json

load_dotenv()

<<<<<<< HEAD
def generate_answer(question: str, report_text: str, script_text: str, call_id: str):
=======
### detect_intent function to classify user intent into categories (order, faq, general, escalation)

def detect_intent(client, model, user_input):
    prompt = f"""
Classify the user's intent into one of:
order
faq
general
escalation

User input:
{user_input}

Return ONLY the label.
"""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip().lower()
####

#### HELPER FUNCTIONS FOR ORDER FLOW
def is_confirmation(text):
    keywords = ["confirm", "place the order", "that's correct", "proceed"]
    return any(k in text.lower() for k in keywords)

def is_cancellation(text):
    keywords = ["cancel", "remove", "never mind"]
    return any(k in text.lower() for k in keywords)
####

def generate_answer(question: str, report_path: str, script_path: str, call_id: str):
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("LLM_MODEL")

<<<<<<< HEAD
    # 1. Local State & Context
    transcript = get_transcript(call_id)
    state = get_call_state(call_id)
    relevant_chunk = find_relevant_chunk(question, report_text)

    # Extract only the TONE part to prevent LLM from repeating the greeting
    try:
        if "TONE:" in script_text:
            tone_instruction = script_text.split("TONE:")[1].strip()
        else:
            tone_instruction = script_text
    except Exception:
        tone_instruction = "Professional and helpful."

    # 3. SINGLE SHOT LLM CALL (Compresses Intent, Extract, & Answer into 1 turn)
    system_prompt = f"""
You are an advanced AI Voice Assistant. You must respond ONLY with a raw JSON object.
Analyze the CONVERSATION HISTORY and the USER'S LATEST TURN.

Categorize the user's latest turn into ONE of these intents: "order_add", "order_confirm", "order_cancel", "escalation", "faq".

- If 'order_add': Extract items to the 'extracted_items' list. Draft a 'speak_reply' confirming the item.
- If 'order_confirm': 'speak_reply' should confirm their order.
- If 'order_cancel': 'speak_reply' should agree to cancel.
- If 'escalation': Choose this ONLY IF the user explicitly asks to speak to a human, manager, or representative, or if they are extremely angry. 'speak_reply' should explicitly say "Please hold while I transfer you to a human."
- If 'faq': Answer their question strictly based on the BUSINESS KNOWLEDGE. If the user's speech is unclear, confusing, or doesn't make sense (e.g., misheard speech), categorize as 'faq' and politely ask them to clarify. DO NOT makeup facts.

Follow this TONE explicitly for your 'speak_reply':
{tone_instruction}

BUSINESS KNOWLEDGE:
{relevant_chunk}

JSON STRUCTURE REQUIRED:
{{
  "intent": "string (one of the 5 allowed intents)",
  "speak_reply": "string (your natural language spoken response)",
  "extracted_items": [
     {{"name": "string", "quantity": "integer"}}
  ]
}}
"""
    
    # We send the unified prompt
    response = client.chat.completions.create(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CONVERSATION HISTORY:\n{transcript}\n\nUSER'S LATEST TURN:\n{question}"}
        ]
    )

    try:
        data = json.loads(response.choices[0].message.content)
        intent = data.get("intent", "faq").lower()
        speak = data.get("speak_reply", "I'm sorry, I encountered an error answering that.")
        items = data.get("extracted_items", [])
    except Exception as e:
        intent = "faq"
        speak = "I did not understand that."
        items = []

    # 4. State Execution based on the single LLM payload
    if intent == "escalation":
        return {"intent": "escalation", "speak": "Please hold while I transfer you.", "order": None}

    if intent == "order_cancel":
        reset_call_state(call_id)
        return {"intent": "order", "speak": speak, "order": None}

    if intent == "order_confirm":
        if state["order_draft"]:
            order_data = {"items": state["order_draft"], "confirmed": True}
            reset_call_state(call_id)
            return {"intent": "order", "speak": speak, "order": order_data}
        else:
            return {"intent": "order", "speak": "You don't have anything in your order yet. What would you like to order?", "order": None}

    if intent == "order_add":
        if items:
            state["order_draft"].extend(items)
        
        # Keep the conversation moving if they didn't finish an order
        if not speak.strip().endswith("?"):
             speak += " Would you like to confirm this order?"
             
        return {"intent": "order", "speak": speak, "order": None}

    # If it's pure FAQ or anything else
    if not speak.strip().endswith("?"):
        speak += " Is there anything else I can help you with?"

    return {"intent": "faq", "speak": speak, "order": None}
=======
    with open(report_path, "r", encoding="utf-8") as f:
        report_text = f.read()

    with open(script_path, "r", encoding="utf-8") as f:
        script_text = f.read()

    # -------- Intent Detection --------
    intent = detect_intent(client, model, question)
    state = get_call_state(call_id)

    # -------- Escalation --------
    if intent == "escalation":
        return {
            "intent": "escalation",
            "speak": "Please hold while I transfer you to a human representative.",
            "order": None
        }

    # -------- Order Flow --------
    if intent == "order":

        # Cancellation
        if is_cancellation(question):
            reset_call_state(call_id)
            return {
                "intent": "order",
                "speak": "Your order has been canceled. Is there anything else I can help you with?",
                "order": None
            }

        # Confirmation
        if is_confirmation(question) and state["order_draft"]:
            order_data = {
                "items": state["order_draft"],
                "confirmed": True
            }

            reset_call_state(call_id)

            return {
                "intent": "order",
                "speak": "Your order has been confirmed. Thank you.",
                "order": order_data
            }

        # Extract items
        extraction_prompt = f"""
Extract ordered items from this sentence.
Return JSON list like:
[
  {{"name": "item name", "quantity": number}}
]

Sentence:
{question}
"""

        extraction = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": extraction_prompt}]
        ).choices[0].message.content

        try:
            items = json.loads(extraction)
            state["order_draft"].extend(items)
        except:
            pass

        draft_summary = ", ".join(
            [f"{i['quantity']} {i['name']}" for i in state["order_draft"]]
        )

        return {
            "intent": "order",
            "speak": f"You have ordered {draft_summary}. Would you like to confirm this order?",
            "order": None
        }

    # -------- FAQ / General Flow --------
    relevant_chunk = find_relevant_chunk(question, report_text)

    answer_prompt = f"""
Follow this greeting and tone:
{script_text}

Answer ONLY using this knowledge:
{relevant_chunk}

Question:
{question}
"""

    answer = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": answer_prompt}]
    ).choices[0].message.content

    answer += " Is there anything else I can help you with?"

    return {
        "intent": intent,
        "speak": answer,
        "order": None
    }
#def generate_answer(question: str, report_path: str, script_path: str) -> str:
#     client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#     model = os.getenv("LLM_MODEL")

#     with open(report_path, "r", encoding="utf-8") as f:
#         report_text = f.read()

#     with open(script_path, "r", encoding="utf-8") as f:
#         script_text = f.read()

# #     # Retrieve most relevant part of the report
# #     relevant_chunk = find_relevant_chunk(question, report_text)

# #     prompt = f"""
# # You are a customer support voice assistant.

# # Follow this greeting and tone exactly:
# # {script_text}

# # You MUST answer using ONLY the information written in the KNOWLEDGE section.
# # Do NOT add explanations.
# # Do NOT infer anything.
# # Do NOT rephrase meaning.

# # If the knowledge does not contain the answer, say:
# # "Let me check that for you."

# # KNOWLEDGE:
# # {relevant_chunk}

# # QUESTION:
# # {question}
# # """

# #     response = client.chat.completions.create(
# #         model=model,
# #         messages=[{"role": "user", "content": prompt}]
# #     )

# #     return response.choices[0].message.content


#     # Retrieve relevant section
#     relevant_chunk = find_relevant_chunk(question, report_text)

#     # Ask GPT if clarification is needed
#     check_prompt = f"""
# You are checking if a customer question is ambiguous.

# Knowledge:
# {relevant_chunk}

# Question:
# {question}

# If the question could refer to multiple different things in the knowledge,
# reply ONLY with:
# CLARIFY

# Otherwise reply ONLY with:
# CLEAR
# """

#     check = client.chat.completions.create(
#         model=model,
#         messages=[{"role": "user", "content": check_prompt}]
#     ).choices[0].message.content.strip()

#     # If ambiguous → ask clarification
#     if "CLARIFY" in check:
#         clarify_prompt = f"""
# Using the knowledge below, ask a short clarification question to the customer.

# Knowledge:
# {relevant_chunk}

# Original Question:
# {question}
# """

#         clarification = client.chat.completions.create(
#             model=model,
#             messages=[{"role": "user", "content": clarify_prompt}]
#         ).choices[0].message.content

#         return clarification

#     # Step 3: If clear → answer normally
#     answer_prompt = f"""
# Follow this greeting and tone:
# {script_text}

# Answer ONLY using this knowledge:
# {relevant_chunk}

# Question:
# {question}
# """

#     answer = client.chat.completions.create(
#         model=model,
#         messages=[{"role": "user", "content": answer_prompt}]
#     ).choices[0].message.content

#     return answer
>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
