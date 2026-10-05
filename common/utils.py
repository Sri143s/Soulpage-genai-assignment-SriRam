import json
import re
from typing import Any, Dict, List, Optional

def clean_json_string(text: str) -> str:
    """
    Extracts JSON from markdown code blocks or raw text strings.
    """
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text

def parse_json_safely(text: str) -> Optional[Dict[str, Any]]:
    """
    Safely parses text to dictionary, returning None if parsing fails.
    """
    try:
        cleaned = clean_json_string(text)
        return json.loads(cleaned)
    except Exception:
        return None

def format_sources(sources: List[Dict[str, Any]]) -> str:
    """
    Formats a list of source dicts into markdown links.
    """
    if not sources:
        return "No external sources cited."
    
    formatted = []
    for idx, src in enumerate(sources, 1):
        title = src.get("title", "Source")
        url = src.get("url", "#")
        source_name = src.get("source", "Web")
        formatted.append(f"{idx}. [{title}]({url}) ({source_name})")
    return "\n".join(formatted)

def sanitize_input(text: str) -> str:
    """
    Sanitizes user input string.
    """
    return text.strip() if text else ""
