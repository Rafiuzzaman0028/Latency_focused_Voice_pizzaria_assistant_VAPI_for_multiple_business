import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_ai_report(raw_text: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("LLM_MODEL")

    prompt = f"""
You are preparing knowledge for an AI voice agent.

From the following company document, create a SMALL, CLEAN, STRUCTURED report
that an AI agent can use to answer customer questions.

Organize into:
- Company Overview
- Services
- Pricing
- Policies
- FAQs
- Tone of speaking

Document:
{raw_text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content