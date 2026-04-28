# SaaS Backend Handover & API Guide

## 📡 System Overview & Project Scope
This repository contains the **AI Core Microservice** for a Multi-Tenant Voice Agent SaaS. 
It sits between Twilio (handling the phone lines) and OpenAI (handling the conversational intelligence). 

**Architecture:** The AI operates as a completely independent, "Black Box" microservice. It manages its own internal database and file storage. **You do not need to touch, edit, or deploy any Python code.** Your backend will simply interface with this AI engine via standard REST APIs, exactly like you would with Stripe or OpenAI.

---

## 🔌 Core API Endpoints for Backend Integration

To build the SaaS Dashboard and manage businesses, you will exclusively use the following endpoints exposed by the AI Microservice:

### 1. Onboarding a Business: `POST /upload-doc/`
- **Purpose:** When a business user signs up on your dashboard, send their rules/menu document to this endpoint via `multipart/form-data`.
- **Required Form Fields:** 
  - `file`: The `.pdf`, `.docx`, or `.txt` document.
  - `business_name`: String
  - `twilio_phone_number`: String (Must be exact E.164 format, e.g., +15551234567)
  - `manager_phone`: String (For human escalations)
- **What it does:** The AI automatically ingests the document, generates a conversational persona, and saves the business profile to its internal database.
- **Returns:** A JSON object containing the unique `tenant_id` and the generated AI profile. Save this `tenant_id` in your primary SaaS database!

### 2. Fetching Orders: `GET /api/orders/{tenant_id}`
- **Purpose:** Retrieve all finalized orders and call summaries for a specific business to display on your SaaS frontend.
- **What it does:** When a customer places an order over the phone, the AI mathematically extracts a structured JSON cart and saves it. This endpoint returns all those JSON files.
- **Returns:** A JSON array of all orders and call transcripts tied to that `tenant_id`.

### 3. Fetching Raw Logs: `GET /api/call-logs/{tenant_id}`
- **Purpose:** Retrieve the raw, un-summarized conversation transcripts for analytics or monitoring.
- **Returns:** A JSON array of call logs tied to the `tenant_id`.

---

## 📞 Twilio Webhook Configuration

To connect the phone lines to the AI, you must configure the business's Twilio Phone Number in the Twilio Console with the following Webhooks:

1. **A Call Comes In:** Point this to `POST <AI_DOMAIN>/voice`
   - *This triggers the AI to look up the business profile and say the greeting.*
2. **Call Status Changes (Status Callback):** Point this to `POST <AI_DOMAIN>/call-end` (Select "Completed")
   - *This is CRITICAL. It tells the AI the call has ended so it can generate the final JSON order and summary.*

**(Note: The ongoing conversation logic is handled automatically via Twilio TwiML routing to `/voice-process`. You do not need to configure that in the dashboard).**
