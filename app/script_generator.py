import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def generate_voice_script(ai_report_text: str) -> str:
    """
    Generates only:
    - Assistant greeting
    - Speaking tone

    This file is meant to be editable later from frontend.
    """

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("LLM_MODEL")

    prompt = f"""
From the following company knowledge report, create ONLY:

1. A short greeting message the AI assistant will say when a call starts.
2. The speaking tone the assistant should follow (professional, polite, friendly, etc).

Keep it very short and clear.

Format exactly like:

GREETING:
<one short greeting sentence>

TONE:
<how the assistant should speak>

Company Knowledge Report:
{ai_report_text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content