import sys
import json
import urllib.request
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathematics.ir_core.proof_ir import ProofGoalIR
from mathematics.verifier import VerificationResult, VerificationStatus
from mathematics.translator.exceptions import TranslationError, FormalizationFailure
from mathematics.llm_translator.client import OpenAICompatibleClient
from mathematics.llm_translator.parser import extract_json_object
from mathematics.llm_translator.repair_loop import AutoFormalizationLoop


@patch("urllib.request.urlopen")
def test_openai_compatible_client_success(mock_urlopen):
    """Verify OpenAICompatibleClient performs HTTP requests and parses response."""
    # Mock response object
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "content": '{"proof_script": "exact H_squared", "reasoning": "proof"}'
                    }
                }
            ]
        }
    ).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    client = OpenAICompatibleClient(
        api_url="http://mock-api.com/v1", api_key="secret", model_name="gpt-4o"
    )
    raw_response = client.generate("system prompt", "user prompt")

    assert "exact H_squared" in raw_response
    mock_urlopen.assert_called_once()


@patch("urllib.request.urlopen")
def test_openai_compatible_client_http_error(mock_urlopen):
    """Verify client wraps urllib errors in TranslationError."""
    mock_urlopen.side_effect = urllib.error.URLError("connection refused")

    client = OpenAICompatibleClient(
        api_url="http://mock-api.com/v1", api_key="secret", model_name="gpt-4o"
    )
    with pytest.raises(TranslationError, match="request failed"):
        client.generate("system prompt", "user prompt")


def test_extract_json_object():
    """Verify robust regex extraction of JSON blocks."""
    # Standard raw JSON
    raw_json = '{"proof_script": "rfl", "reasoning": "none"}'
    assert extract_json_object(raw_json) == {
        "proof_script": "rfl",
        "reasoning": "none",
    }

    # Markdown wrapped JSON
    wrapped_json = (
        "Here is the proof:\n"
        "```json\n"
        '{"proof_script": "exact H_squared", "reasoning": "success"}\n'
        "```\n"
        "Hope this helps!"
    )
    assert extract_json_object(wrapped_json) == {
        "proof_script": "exact H_squared",
        "reasoning": "success",
    }

    # Wrapped JSON without json prefix
    wrapped_json_no_prefix = (
        "```\n" '{"proof_script": "exact H_squared", "reasoning": "success"}\n' "```"
    )
    assert extract_json_object(wrapped_json_no_prefix) == {
        "proof_script": "exact H_squared",
        "reasoning": "success",
    }

    # JSON with surrounding text without backticks
    text_surrounding = (
        "Some introduction text before "
        '{"proof_script": "rfl", "reasoning": "inline"} '
        "and some explanation after."
    )
    assert extract_json_object(text_surrounding) == {
        "proof_script": "rfl",
        "reasoning": "inline",
    }

    # Invalid JSON raises TranslationError
    invalid_json = "This is not a JSON block."
    with pytest.raises(TranslationError, match="Failed to decode"):
        extract_json_object(invalid_json)


def test_repair_loop_immediate_success():
    """Verify repair loop returns immediately on first-attempt success."""
    mock_client = MagicMock()
    mock_client.generate.return_value = '{"proof_script": "rfl", "reasoning": "proof"}'

    mock_evaluator = MagicMock()
    mock_evaluator.evaluate.return_value = VerificationResult(
        status=VerificationStatus.VERIFIED, output="Success", execution_time_ms=50
    )

    loop = AutoFormalizationLoop(mock_client, mock_evaluator)

    goal = ProofGoalIR(
        goal_id="nat_zero",
        domain="mathematics",
        theorem_statement="n + 0 = n",
        assumptions=[],
        source_reference="test",
    )

    res, proof_script, attempts = loop.run(goal, max_attempts=3)

    assert res.status == VerificationStatus.VERIFIED
    assert proof_script == "rfl"
    assert len(attempts) == 1
    assert attempts[0].attempt_number == 1
    assert attempts[0].proof_script == "rfl"
    assert attempts[0].verification_status == VerificationStatus.VERIFIED


def test_repair_loop_success_with_correction():
    """Verify repair loop runs multiple attempts utilizing correction feedback."""
    mock_client = MagicMock()
    # 1st attempt: return wrong proof; 2nd attempt: return correct proof
    mock_client.generate.side_effect = [
        '{"proof_script": "exact wrong_axiom", "reasoning": "wrong"}',
        '{"proof_script": "exact H_squared", "reasoning": "corrected"}',
    ]

    mock_evaluator = MagicMock()
    mock_evaluator.evaluate.side_effect = [
        # 1st eval: compile error
        VerificationResult(
            status=VerificationStatus.COMPILATION_ERROR,
            output="",
            error_details="unknown constant 'wrong_axiom'",
            execution_time_ms=30,
        ),
        # 2nd eval: verified
        VerificationResult(
            status=VerificationStatus.VERIFIED, output="Success", execution_time_ms=40
        ),
    ]

    loop = AutoFormalizationLoop(mock_client, mock_evaluator)

    goal = ProofGoalIR(
        goal_id="h_h_ident",
        domain="quantum",
        theorem_statement="H ⬝ H = I",
        assumptions=[],
        source_reference="test",
    )

    res, proof_script, attempts = loop.run(goal, max_attempts=3)

    assert res.status == VerificationStatus.VERIFIED
    assert proof_script == "exact H_squared"
    assert len(attempts) == 2
    assert attempts[0].attempt_number == 1
    assert attempts[0].proof_script == "exact wrong_axiom"
    assert attempts[0].verification_status == VerificationStatus.COMPILATION_ERROR
    assert attempts[0].lean_output == "unknown constant 'wrong_axiom'"
    assert attempts[1].attempt_number == 2
    assert attempts[1].verification_status == VerificationStatus.VERIFIED

    # Check correction prompt generation
    mock_client.generate.assert_called()
    assert mock_client.generate.call_count == 2
    # Verify second prompt contains compilation error feedback
    last_user_prompt = mock_client.generate.call_args[0][1]
    assert "unknown constant 'wrong_axiom'" in last_user_prompt


def test_repair_loop_exceeds_max_attempts():
    """Verify repair loop raises FormalizationFailure on limit exceeded."""
    mock_client = MagicMock()
    mock_client.generate.return_value = (
        '{"proof_script": "sorry", "reasoning": "failed"}'
    )

    mock_evaluator = MagicMock()
    mock_evaluator.evaluate.return_value = VerificationResult(
        status=VerificationStatus.UNSOLVED_GOALS,
        output="",
        error_details="sorry used",
        execution_time_ms=20,
    )

    loop = AutoFormalizationLoop(mock_client, mock_evaluator)

    goal = ProofGoalIR(
        goal_id="impossible",
        domain="physics",
        theorem_statement="0 = 1",
        assumptions=[],
        source_reference="test",
    )

    with pytest.raises(FormalizationFailure) as exc_info:
        loop.run(goal, max_attempts=3)

    assert "Auto-formalization failed" in str(exc_info.value)
    assert len(exc_info.value.attempts) == 3
    assert exc_info.value.attempts[2].attempt_number == 3
    assert (
        exc_info.value.attempts[2].verification_status
        == VerificationStatus.UNSOLVED_GOALS
    )
