import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from mathematics.translator.exceptions import TranslationError


class LLMClient(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Sends a request to the LLM and returns the raw string response."""
        pass


class OpenAICompatibleClient(LLMClient):
    def __init__(
        self,
        api_url: str,
        api_key: str,
        model_name: str,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generates content via an HTTP POST request to an OpenAI-compatible endpoint."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
        }

        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                resp_data = json.loads(response.read().decode("utf-8"))
                return resp_data["choices"][0]["message"]["content"]
        except urllib.error.URLError as e:
            raise TranslationError(f"LLM API request failed: {str(e)}") from e
        except Exception as e:
            raise TranslationError(
                f"Unexpected error when calling LLM API: {str(e)}"
            ) from e
