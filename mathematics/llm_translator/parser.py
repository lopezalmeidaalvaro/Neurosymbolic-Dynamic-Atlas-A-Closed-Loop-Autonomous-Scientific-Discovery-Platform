import json
import re
from mathematics.translator.exceptions import TranslationError


def extract_json_object(raw_response: str) -> dict:
    """Extracts the first JSON object from a raw response string.

    It ignores Markdown block wrappers and peripheral text.
    """
    # 1. Search for JSON block enclosed in markdown tags ```json ... ```
    match_markdown = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```", raw_response, re.DOTALL | re.IGNORECASE
    )
    if match_markdown:
        candidate = match_markdown.group(1)
    else:
        # 2. Fallback: Search for first opening curly brace to last closing curly brace
        match_curly = re.search(r"(\{.*\})", raw_response, re.DOTALL)
        if match_curly:
            candidate = match_curly.group(1)
        else:
            candidate = raw_response.strip()

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise TranslationError(
            f"Failed to decode JSON from extracted block. Error: {str(e)}\nRaw was: '{raw_response}'"
        ) from e
