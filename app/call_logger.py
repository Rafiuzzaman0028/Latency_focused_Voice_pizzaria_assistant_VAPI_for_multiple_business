import os


def save_call_log(call_id: str, transcript: str):
    os.makedirs("call_logs", exist_ok=True)
    with open(f"call_logs/{call_id}.txt", "w", encoding="utf-8") as f:
        f.write(transcript)
