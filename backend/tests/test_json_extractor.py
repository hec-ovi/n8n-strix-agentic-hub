"""Unit tests for JSON extraction helpers."""

import pytest

from src.lib.json_extractor import extract_json_object


def test_extract_json_object_from_plain_json() -> None:
    """Extractor should return the original JSON object when already clean."""
    payload = '{"title":"Test","value":1}'

    result = extract_json_object(payload)

    assert result == payload


def test_extract_json_object_from_wrapped_payload() -> None:
    """Extractor should isolate the JSON object from surrounding text."""
    payload = "Here is the answer:\n```json\n{\"title\":\"Test\",\"value\":1}\n```"

    result = extract_json_object(payload)

    assert result == '{"title":"Test","value":1}'


def test_extract_json_object_raises_when_missing() -> None:
    """Extractor should fail when no JSON object exists."""
    with pytest.raises(ValueError):
        extract_json_object("No JSON here.")
