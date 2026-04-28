import json
import os
import uuid
from typing import Dict, Any, List

DB_PATH = "mock_database.json"

def _load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_PATH):
        return {
            "tenants": {},
            "orders": [],
            "call_logs": []
        }
    with open(DB_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"tenants": {}, "orders": [], "call_logs": []}

def _save_db(data: Dict[str, Any]):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

import re

def normalize_phone(phone: str) -> str:
    if not phone:
        return ""
    return re.sub(r'[\s\-\(\)]', '', phone)

# --- TENANT (BUSINESS) FUNCTIONS ---

def save_tenant(twilio_phone_number: str, business_name: str, manager_phone: str, report_text: str, script_text: str) -> str:
    """Saves or updates a business tenant based on their Twilio Phone Number."""
    db = _load_db()
    
    tenant_id = str(uuid.uuid4())
    norm_twilio = normalize_phone(twilio_phone_number)
    
    # Check if tenant exists by phone number and update if so
    for t_id, t_data in db["tenants"].items():
        if normalize_phone(t_data.get("twilio_phone_number", "")) == norm_twilio:
            tenant_id = t_id
            break

    db["tenants"][tenant_id] = {
        "tenant_id": tenant_id,
        "twilio_phone_number": norm_twilio, # Save normalized
        "business_name": business_name,
        "manager_phone": normalize_phone(manager_phone),
        "report_text": report_text,
        "script_text": script_text
    }
    _save_db(db)
    return tenant_id

def get_tenant_by_twilio_number(twilio_phone_number: str) -> dict:
    """Returns the tenant config. Used by voice webhooks to dynamically route."""
    db = _load_db()
    norm_twilio = normalize_phone(twilio_phone_number)
    for t_id, t_data in db["tenants"].items():
        if normalize_phone(t_data.get("twilio_phone_number", "")) == norm_twilio:
            return t_data
    return None

# --- ORDERS FUNCTIONS ---

def insert_order(tenant_id: str, caller_phone: str, call_id: str, order_json: dict):
    db = _load_db()
    order_entry = {
        "order_id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "caller_phone": caller_phone,
        "call_id": call_id,
        "order_data": order_json,
        "status": "pending"
    }
    db["orders"].append(order_entry)
    _save_db(db)

def get_order_by_call_id(call_id: str) -> dict:
    db = _load_db()
    for order in db["orders"]:
        if order.get("call_id") == call_id:
            return order
    return None

# --- CALL LOGS FUNCTIONS ---

def save_db_call_log(tenant_id: str, caller_phone: str, call_id: str, transcript: str):
    db = _load_db()
    log_entry = {
        "call_id": call_id,
        "tenant_id": tenant_id,
        "caller_phone": caller_phone,
        "transcript": transcript
    }
    db["call_logs"].append(log_entry)
    _save_db(db)
