from fastapi import APIRouter

router = APIRouter()

RESOURCES = [
    {
        "category": "stress",
        "title": "Grounding pause",
        "description": "Name five things you see, four you feel, three you hear, two you smell, and one you taste.",
    },
    {
        "category": "anxiety",
        "title": "Slow breathing",
        "description": "Try a gentle exhale that is slightly longer than your inhale for one minute.",
    },
    {
        "category": "depression support",
        "title": "Small next step",
        "description": "Choose one manageable action and consider contacting someone you trust.",
    },
    {
        "category": "productivity",
        "title": "Ten-minute start",
        "description": "Shrink a task to a ten-minute first step, then reassess without judgment.",
    },
    {
        "category": "emergency support",
        "title": "Immediate safety",
        "description": "If you are in immediate danger, contact local emergency services and a trusted person now.",
    },
]


@router.get("/")
def list_resources(category: str | None = None) -> dict:
    items = RESOURCES
    if category:
        items = [item for item in items if item["category"].lower() == category.lower()]
    return {
        "resources": items,
        "disclaimer": "These resources are educational and are not a replacement for professional care.",
    }
