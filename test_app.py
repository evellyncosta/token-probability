import os
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from app import app


def fake_message(content="world", tokens=None):
    tokens = tokens or ["wor", "ld"]
    logprob_content = []
    for token in tokens:
        logprob_content.append(
            {
                "token": token,
                "logprob": -0.1,
                "top_logprobs": [
                    {"token": token, "logprob": -0.1},
                    {"token": "other", "logprob": -2.3},
                ],
            }
        )
    return SimpleNamespace(
        content=content,
        response_metadata={
            "logprobs": {
                "content": logprob_content
            }
        },
    )


class GenerateRouteTests(TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_missing_server_key_returns_safe_configuration_error(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.post("/api/generate", json={"prompt": "Hello"})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {"error": "OpenAI API key is not configured on the server."},
        )

    @patch("app.ChatOpenAI")
    def test_generates_token_probabilities_without_browser_credentials(self, chat_openai):
        chat_openai.return_value.invoke.return_value = fake_message()

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post(
                "/api/generate",
                json={"prompt": "Hello", "top_k": 5, "temperature": 0.0},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["text"], "world")
        self.assertEqual(len(response.get_json()["tokenProbs"]), 2)
        self.assertEqual(
            "".join(item["selected_token"] for item in response.get_json()["tokenProbs"]),
            "world",
        )
        token = response.get_json()["tokenProbs"][0]
        self.assertEqual(token["selected_token"], "wor")
        self.assertIn("selected_prob", token)
        self.assertEqual(len(token["top_logprobs"]), 2)
        chat_openai.assert_called_once_with(
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=16,
            logprobs=True,
            top_logprobs=5,
        )

    @patch("app.ChatOpenAI")
    def test_provider_errors_do_not_expose_configuration(self, chat_openai):
        chat_openai.return_value.invoke.side_effect = Exception("secret-key")

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post("/api/generate", json={"prompt": "Hello"})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.get_json(), {"error": "OpenAI generation request failed."})

    @patch("app.ChatOpenAI")
    def test_rejects_multiple_words_without_truncating_tokens(self, chat_openai):
        chat_openai.return_value.invoke.return_value = fake_message(
            "two words", ["two", " words"]
        )
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post("/api/generate", json={"prompt": "Hello"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"error": "OpenAI did not return a valid next word."})

    @patch("app.ChatOpenAI")
    def test_rejects_punctuation_without_altering_tokens(self, chat_openai):
        chat_openai.return_value.invoke.return_value = fake_message("word!", ["word", "!"])
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post("/api/generate", json={"prompt": "Hello"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"error": "OpenAI did not return a valid next word."})
