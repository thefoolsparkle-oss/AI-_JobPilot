import json
import logging

logger = logging.getLogger(__name__)


def extract_json(response: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    if not response:
        return {}
    text = response.strip()
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        text = text[start:end].strip()
    elif "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        text = text[start:end].strip()
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"JSON parse failed: {e}")
        return {}
