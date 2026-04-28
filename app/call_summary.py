import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def generate_summary(call_id: str, transcript: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
Summarize this phone call between customer and AI assistant.

Conversation:
{transcript}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    summary = res.choices[0].message.content

    os.makedirs("call_summaries", exist_ok=True)
    with open(f"call_summaries/{call_id}.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    return summary
