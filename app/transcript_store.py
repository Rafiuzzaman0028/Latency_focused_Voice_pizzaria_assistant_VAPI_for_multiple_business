<<<<<<< HEAD
=======
# # Stores live transcript in memory during call
# live_calls = {}


# def add_line(call_id: str, speaker: str, text: str):
#     if call_id not in live_calls:
#         live_calls[call_id] = []

#     live_calls[call_id].append(f"{speaker}: {text}")


# def get_transcript(call_id: str):
#     return "\n".join(live_calls.get(call_id, []))


# def clear_call(call_id: str):
#     if call_id in live_calls:
#         del live_calls[call_id]



>>>>>>> 108272368b09ce1dbae5fa86378a68c296436a4f
from collections import defaultdict

# Global memory for active calls
CALL_TRANSCRIPTS = defaultdict(list)

# Add call state memory (for order flow)
CALL_STATE = defaultdict(lambda: {
    "order_draft": [],
    "awaiting_confirmation": False
})

def get_call_state(call_id: str):
    return CALL_STATE[call_id]

def reset_call_state(call_id: str):
    CALL_STATE[call_id] = {
        "order_draft": [],
        "awaiting_confirmation": False
    }

#### 

def add_line(call_id: str, speaker: str, text: str):
    """Add a line to the call transcript."""
    CALL_TRANSCRIPTS[call_id].append(f"{speaker}: {text}")


def get_transcript(call_id: str) -> str:
    """Return full transcript as string."""
    return "\n".join(CALL_TRANSCRIPTS.get(call_id, []))


def clear_call(call_id: str):
    """Remove transcript after call ends."""
    if call_id in CALL_TRANSCRIPTS:
        del CALL_TRANSCRIPTS[call_id]
