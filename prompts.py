from typing import Dict, Tuple

from langchain_core.prompts import PromptTemplate


DEFAULT_LOCALE = "pt-BR"
SUPPORTED_LOCALES = {"pt-BR", "en"}
LOCALE_INSTRUCTIONS = {
    "pt-BR": "Respond in Brazilian Portuguese.",
    "en": "Respond in English.",
}

WORD_PROMPT_TEMPLATE = PromptTemplate.from_template(
    "You are a next-word predictor. Given the user's text context, return "
    "exactly one lexical word that naturally continues it. Return only the "
    "word, with no punctuation, quotation marks, markdown, explanation, or "
    "additional words. If the context does not end in whitespace, you may "
    "include one leading space needed to continue it. {locale_instruction}"
)
MAX_WORD_TOKENS = 16

TEXT_PROMPT_TEMPLATE = PromptTemplate.from_template(
    "Answer the user's request in plain text only. Do not use Markdown, headings, "
    "lists, code fences, or inline formatting. Paragraphs are allowed when useful. "
    "Aim for a complete answer of no more than 500 characters. {locale_instruction}"
)
MAX_TEXT_TOKENS = 256

PATH_PROMPT_TEMPLATE = PromptTemplate.from_template(
    "Continue the user's text with the next token only. Preserve natural text and "
    "pay attention to the ponctuation and conciseness of the text, do not forget to answer with space if necessary "
    "spacing exactly: when the next token begins a new word after a word or "
    "sentence-ending punctuation, include the required leading whitespace in that "
    "token. Do not join lexical words together. Keep punctuation attached only when "
    "it naturally follows the preceding text. Return no explanation, quotation "
    "marks, Markdown, or additional tokens. {locale_instruction}"
)
MAX_PATH_TOKENS = 1

GENERATION_PROFILES = {
    "word": (WORD_PROMPT_TEMPLATE, MAX_WORD_TOKENS),
    "text": (TEXT_PROMPT_TEMPLATE, MAX_TEXT_TOKENS),
    "path": (PATH_PROMPT_TEMPLATE, MAX_PATH_TOKENS),
}


def normalize_locale(locale: object) -> str:
    return locale if isinstance(locale, str) and locale in SUPPORTED_LOCALES else DEFAULT_LOCALE


def get_generation_profile(mode: str, locale: str = DEFAULT_LOCALE) -> Tuple[str, int]:
    try:
        prompt_template, max_tokens = GENERATION_PROFILES[mode]
    except KeyError as error:
        raise ValueError("Generation mode must be 'word', 'text', or 'path'.") from error

    locale_instruction = LOCALE_INSTRUCTIONS[normalize_locale(locale)]
    return prompt_template.format(locale_instruction=locale_instruction), max_tokens
