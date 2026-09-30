import os
import uuid
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from app import (
    app,
    get_generation_error_code,
    tokenize_prompt,
)
from prompts import (
    MAX_PATH_TOKENS,
    MAX_TEXT_TOKENS,
    MAX_WORD_TOKENS,
    PATH_PROMPT_TEMPLATE,
    TEXT_PROMPT_TEMPLATE,
    get_generation_profile,
    normalize_locale,
)


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
        self.encoding_for_model = patch("app.tiktoken.encoding_for_model")
        encoding = self.encoding_for_model.start()
        encoding.return_value.encode.side_effect = lambda text: list(
            text.encode("utf-8")
        )
        encoding.return_value.decode_single_token_bytes.side_effect = (
            lambda token_id: bytes([token_id])
        )
        self.addCleanup(self.encoding_for_model.stop)

    def assert_request_id_header(self, response):
        request_id = response.headers.get("X-Request-ID")
        self.assertIsNotNone(request_id)
        uuid.UUID(request_id)
        return request_id

    def test_mode_pages_and_navigation(self):
        home = self.client.get("/")
        tokens = self.client.get("/tokens")
        text = self.client.get("/text")
        path = self.client.get("/hallucination-path")
        phrase = self.client.get("/phrase")

        self.assertEqual(home.status_code, 200)
        self.assertIn(b"Visualizar token", home.data)
        self.assertIn(b'href="/tokens"', home.data)
        self.assertIn(b"Visualizar texto", home.data)
        self.assertIn(b'href="/text"', home.data)
        self.assertIn(b"Hallucination Path", home.data)
        self.assertIn(b'href="/hallucination-path"', home.data)
        self.assertEqual(tokens.status_code, 200)
        self.assertIn(b"Digite o contexto", tokens.data)
        self.assertNotIn(b"o gato subiu no", tokens.data)
        self.assertIn(b'href="/"', tokens.data)
        self.assertEqual(text.status_code, 200)
        self.assertIn(b"Pergunta ou instru", text.data)
        self.assertNotIn(b"Em constru", text.data)
        self.assertEqual(path.status_code, 200)
        self.assertIn(b"premissa falsa", path.data)
        self.assertIn(b'href="/"', path.data)
        self.assertEqual(phrase.status_code, 302)
        self.assertIn("/text", phrase.headers["Location"])

    def test_missing_server_key_returns_safe_configuration_error(self):
        with self.assertLogs(app.logger, level="ERROR") as logs:
            with patch.dict(os.environ, {}, clear=True):
                response = self.client.post("/api/generate", json={"prompt": "Hello"})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {"error": "OpenAI API key is not configured on the server."},
        )
        request_id = self.assert_request_id_header(response)
        record = "\n".join(logs.output)
        self.assertIn("ERROR", record)
        self.assertIn(f"request_id={request_id}", record)
        self.assertIn("status=500", record)
        self.assertIn("error_code=openai_api_key_not_configured", record)
        self.assertIn("exception_type=RuntimeError", record)
        self.assertIn("mode=word", record)
        self.assertIn("locale=pt-BR", record)
        self.assertIn("top_k=5", record)
        self.assertIn("temperature=0.0", record)

    def test_validation_failure_is_logged_with_a_correlation_id(self):
        with self.assertLogs(app.logger, level="WARNING") as logs:
            response = self.client.post(
                "/api/generate", json={"prompt": "Hello", "top_k": "invalid"}
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(), {"error": "Generation settings must be numeric."}
        )
        request_id = self.assert_request_id_header(response)
        record = "\n".join(logs.output)
        self.assertIn(f"request_id={request_id}", record)
        self.assertIn("WARNING", record)
        self.assertIn("status=400", record)
        self.assertIn("error_code=generation_settings_invalid", record)
        self.assertIn("exception_type=ValueError", record)
        self.assertIn("mode=word", record)
        self.assertIn("locale=pt-BR", record)

    @patch("app.ChatOpenAI")
    def test_generates_token_probabilities_without_browser_credentials(self, chat_openai):
        chat_openai.return_value.invoke.return_value = fake_message()

        prompt = "PROMPT_MUST_NOT_APPEAR"
        generated_text = "world"
        with self.assertLogs(app.logger, level="INFO") as logs:
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
                response = self.client.post(
                    "/api/generate",
                    json={"prompt": prompt, "top_k": 5, "temperature": 0.0},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["text"], generated_text)
        prompt_tokens = response.get_json()["promptTokens"]
        self.assertTrue(prompt_tokens)
        self.assertEqual(
            b"".join(bytes(item["bytes"]) for item in prompt_tokens),
            prompt.encode("utf-8"),
        )
        self.assertEqual(len(response.get_json()["tokenProbs"]), 2)
        self.assertEqual(
            "".join(item["selected_token"] for item in response.get_json()["tokenProbs"]),
            "world",
        )
        token = response.get_json()["tokenProbs"][0]
        self.assertEqual(token["selected_token"], "wor")
        self.assertIn("selected_prob", token)
        self.assertEqual(len(token["top_logprobs"]), 2)
        record = "\n".join(logs.output)
        self.assertIn("outcome=success", record)
        self.assertIn("request_id=", record)
        self.assertIn("status=200", record)
        self.assertIn("duration_ms=", record)
        self.assertNotIn(prompt, record)
        self.assertNotIn(generated_text, record)
        chat_openai.assert_called_once_with(
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=16,
            logprobs=True,
            top_logprobs=5,
        )

    @patch("app.ChatOpenAI")
    def test_text_mode_allows_paragraphs_and_uses_text_profile(self, chat_openai):
        text = "Feliz aniversário, pai!\n\nQue seu dia seja cheio de alegria."
        chat_openai.return_value.invoke.return_value = fake_message(
            text, ["Feliz aniversário, pai!", "\n\n", "Que seu dia seja cheio de alegria."]
        )

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post(
            "/api/generate",
            json={"prompt": "Escreva uma mensagem", "mode": "text", "locale": "pt-BR"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["text"], text)
        self.assertEqual(
            "".join(item["selected_token"] for item in response.get_json()["tokenProbs"]), text
        )
        chat_openai.assert_called_once_with(
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=MAX_TEXT_TOKENS,
            logprobs=True,
            top_logprobs=5,
        )
        self.assertEqual(
            chat_openai.return_value.invoke.call_args.args[0][0]["content"],
            TEXT_PROMPT_TEMPLATE.format(
                locale_instruction="Respond in Brazilian Portuguese."
            ),
        )

    @patch("app.ChatOpenAI")
    def test_english_locale_instructs_the_model_to_respond_in_english(self, chat_openai):
        chat_openai.return_value.invoke.return_value = fake_message()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post(
                "/api/generate", json={"prompt": "Hello", "locale": "en"}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            chat_openai.return_value.invoke.call_args.args[0][0]["content"],
            get_generation_profile("word", "en")[0],
        )

    @patch("app.ChatOpenAI")
    def test_invalid_locale_uses_portuguese_without_forwarding_it(self, chat_openai):
        chat_openai.return_value.invoke.return_value = fake_message()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post(
                "/api/generate", json={"prompt": "Hello", "locale": "fr"}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(normalize_locale("fr"), "pt-BR")
        self.assertEqual(
            chat_openai.return_value.invoke.call_args.args[0][0]["content"],
            get_generation_profile("word", "pt-BR")[0],
        )

    @patch("app.ChatOpenAI")
    def test_text_mode_rejects_markdown_without_changing_tokens(self, chat_openai):
        chat_openai.return_value.invoke.return_value = fake_message("# Título", ["#", " Título"])
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post(
                "/api/generate", json={"prompt": "Escreva", "mode": "text"}
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"error": "OpenAI did not return plain text."})

    @patch("app.ChatOpenAI")
    def test_text_mode_preserves_responses_over_500_characters(self, chat_openai):
        text = "a" * 501
        chat_openai.return_value.invoke.return_value = fake_message(text, [text])
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post(
                "/api/generate", json={"prompt": "Escreva", "mode": "text"}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["text"], text)
        self.assertEqual(response.get_json()["tokenProbs"][0]["selected_token"], text)

    @patch("app.ChatOpenAI")
    def test_path_mode_returns_one_token_and_uses_path_profile(self, chat_openai):
        chat_openai.return_value.invoke.return_value = fake_message(" it", [" it"])

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post(
                "/api/generate", json={"prompt": "A false premise", "mode": "path"}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["text"], " it")
        self.assertEqual(len(response.get_json()["tokenProbs"]), 1)
        chat_openai.assert_called_once_with(
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=MAX_PATH_TOKENS,
            logprobs=True,
            top_logprobs=5,
        )
        self.assertEqual(
            chat_openai.return_value.invoke.call_args.args[0][0]["content"],
            PATH_PROMPT_TEMPLATE.format(
                locale_instruction="Respond in Brazilian Portuguese."
            ),
        )
        self.assertIn("Do not join lexical words together.", PATH_PROMPT_TEMPLATE.template)
        self.assertIn("leading whitespace", PATH_PROMPT_TEMPLATE.template)

    def test_prompt_templates_render_every_mode_with_the_selected_locale(self):
        expected_token_limits = {
            "word": MAX_WORD_TOKENS,
            "text": MAX_TEXT_TOKENS,
            "path": MAX_PATH_TOKENS,
        }

        for mode, max_tokens in expected_token_limits.items():
            with self.subTest(mode=mode):
                system_prompt, returned_max_tokens = get_generation_profile(mode, "en")

                self.assertEqual(returned_max_tokens, max_tokens)
                self.assertIn("Respond in English.", system_prompt)

    def test_prompt_profile_rejects_an_unknown_mode(self):
        with self.assertRaisesRegex(
            ValueError, "Generation mode must be 'word', 'text', or 'path'."
        ):
            get_generation_profile("unknown")

    @patch("app.ChatOpenAI")
    def test_path_mode_rejects_multiple_tokens(self, chat_openai):
        chat_openai.return_value.invoke.return_value = fake_message(" it is", [" it", " is"])

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post(
                "/api/generate", json={"prompt": "A false premise", "mode": "path"}
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(), {"error": "OpenAI did not return a valid next token."}
        )

    @patch("app.tiktoken.encoding_for_model")
    @patch("app.ChatOpenAI")
    def test_uses_generation_model_tokenizer_for_prompt(self, chat_openai, encoding_for_model):
        encoding_for_model.return_value.encode.return_value = [99]
        encoding_for_model.return_value.decode_single_token_bytes.return_value = b"Hello"
        chat_openai.return_value.invoke.return_value = fake_message()

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post("/api/generate", json={"prompt": "Hello"})

        self.assertEqual(response.status_code, 200)
        encoding_for_model.assert_called_once_with("gpt-4o-mini")
        self.assertEqual(response.get_json()["promptTokens"], [{"id": 99, "bytes": [72, 101, 108, 108, 111]}])

    @patch("app.tiktoken.encoding_for_model", side_effect=KeyError("unknown-model"))
    def test_rejects_unknown_tokenizer_model_without_fallback(self, _encoding_for_model):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            response = self.client.post("/api/generate", json={"prompt": "Hello"})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {"error": "No official tokenizer encoding is configured for the selected OpenAI model."},
        )

    @patch("app.tiktoken.encoding_for_model")
    def test_prompt_tokens_preserve_raw_bytes(self, encoding_for_model):
        encoding_for_model.return_value.encode.return_value = [501, 502]
        encoding_for_model.return_value.decode_single_token_bytes.side_effect = [b" ", b"\xc3"]

        self.assertEqual(
            tokenize_prompt(" placeholder"),
            [{"id": 501, "bytes": [32]}, {"id": 502, "bytes": [195]}],
        )

    @patch("app.ChatOpenAI")
    def test_provider_errors_do_not_expose_configuration(self, chat_openai):
        secret = "OPENAI_API_KEY=secret-key"
        prompt = "PROMPT_MUST_NOT_APPEAR"
        chat_openai.return_value.invoke.side_effect = Exception(secret)

        with self.assertLogs(app.logger, level="ERROR") as logs:
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
                response = self.client.post("/api/generate", json={"prompt": prompt})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.get_json(), {"error": "OpenAI generation request failed."})
        request_id = self.assert_request_id_header(response)
        record = "\n".join(logs.output)
        self.assertIn(f"request_id={request_id}", record)
        self.assertIn("status=502", record)
        self.assertIn("error_code=unexpected_exception", record)
        self.assertIn("exception_type=Exception", record)
        self.assertIn("Traceback", record)
        self.assertNotIn(secret, record)
        self.assertNotIn(prompt, record)

    def test_known_generation_errors_have_safe_diagnostic_codes(self):
        cases = {
            RuntimeError("OpenAI API key is not configured on the server."): (
                "openai_api_key_not_configured"
            ),
            RuntimeError(
                "No official tokenizer encoding is configured for the selected OpenAI model."
            ): "tokenizer_configuration_unsupported",
            RuntimeError("OpenAI did not return token probabilities."): (
                "token_probabilities_missing"
            ),
            RuntimeError("OpenAI did not return a valid next word."): "generated_word_invalid",
            RuntimeError("OpenAI did not return a valid text response."): "generated_text_invalid",
            RuntimeError("OpenAI did not return plain text."): "plain_text_invalid",
            RuntimeError("OpenAI did not return a valid next token."): "generated_token_invalid",
            ValueError("Generation settings must be numeric."): "generation_settings_invalid",
        }

        for error, error_code in cases.items():
            with self.subTest(error=type(error).__name__):
                self.assertEqual(get_generation_error_code(error), error_code)

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
