"""
Curated catalogue of UK-accent ElevenLabs voices.
The frontend calls GET /api/voices to populate a dropdown by name.
The backend uses voice_id when creating/updating VAPI assistants.
"""

VOICE_CATALOGUE = [
    {
        "id": "JBFqnCBsd6RMkjVDRZzb",
        "name": "George",
        "gender": "male",
        "accent": "British",
        "description": "Warm, raspy British male"
    },
    {
        "id": "TX3LPaxmHKxFdv7VOQHJ",
        "name": "Liam",
        "gender": "male",
        "accent": "British",
        "description": "Young, articulate British male"
    },
    {
        "id": "pFZP5JQG7iQjIQuC4Bku",
        "name": "Lily",
        "gender": "female",
        "accent": "British",
        "description": "Warm, clear British female"
    },
    {
        "id": "EXAVITQu4vr4xnSDxMaL",
        "name": "Sarah",
        "gender": "female",
        "accent": "British",
        "description": "Soft, news-reader British female"
    },
    {
        "id": "FGY2WhTYpPnrIDTdsKH5",
        "name": "Laura",
        "gender": "female",
        "accent": "British",
        "description": "Upbeat, friendly British female"
    },
    {
        "id": "bIHbv24MWmeRgasZH58o",
        "name": "Will",
        "gender": "male",
        "accent": "British",
        "description": "Friendly, professional British male"
    },
]

DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George — current hardcoded default


def get_voice_by_id(voice_id: str) -> dict | None:
    """Returns the voice entry if the ID exists in the catalogue, None otherwise."""
    for voice in VOICE_CATALOGUE:
        if voice["id"] == voice_id:
            return voice
    return None


def is_valid_voice_id(voice_id: str) -> bool:
    """Checks whether a voice ID exists in the catalogue."""
    return any(v["id"] == voice_id for v in VOICE_CATALOGUE)
