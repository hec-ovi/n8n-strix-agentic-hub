"""Helpers for extracting JSON payloads from model output."""

import json


def extract_json_object(payload: str) -> str:
    """Extract the first JSON object found in a string payload.

    Args:
        payload: Raw model output that may contain prose or fenced JSON.

    Returns:
        The extracted JSON object as a string.

    Raises:
        ValueError: If no valid JSON object can be located.
    """
    start = payload.find("{")
    end = payload.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in payload.")

    candidate = payload[start : end + 1]
    json.loads(candidate)
    return candidate
