from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import math
import re
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

MODEL_NAME = "gpt-4o-mini"
SYSTEM_PROMPT = (
    "You are a next-word predictor. Given the user's text context, return "
    "exactly one lexical word that naturally continues it. Return only the "
    "word, with no punctuation, quotation marks, markdown, explanation, or "
    "additional words. If the context does not end in whitespace, you may "
    "include one leading space needed to continue it."
)
MAX_WORD_TOKENS = 16
WORD_PATTERN = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)*$", re.UNICODE)


def get_model_response(
    prompt: str, top_k: int = 5, temperature: float = 0.0
) -> Tuple[str, List[Dict]]:
    """
    Returns:
      response_text: str
      token_probs: List[Dict] with per-token:
          {
            "selected_token": str,
            "selected_prob": float,
            "top_logprobs": List[{"token": str, "probability": float}]
          }
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OpenAI API key is not configured on the server.")

    model = ChatOpenAI(
        model=MODEL_NAME,
        temperature=temperature,
        max_tokens=MAX_WORD_TOKENS,
        logprobs=True,
        top_logprobs=top_k,
    )
    response = model.invoke(
        [
            {"role": "developer", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )

    response_text = response.content
    logprobs = response.response_metadata.get("logprobs")

    if not isinstance(response_text, str) or not logprobs or not logprobs.get("content"):
        raise RuntimeError("OpenAI did not return token probabilities.")

    token_probs = []
    for token_info in logprobs["content"]:
        selected_token = token_info["token"]
        selected_prob = math.exp(token_info["logprob"])

        top_items = []
        for lp in token_info["top_logprobs"]:
            top_items.append({
                "token": lp["token"],
                "probability": math.exp(lp["logprob"])
            })

        token_probs.append({
            "selected_token": selected_token,
            "selected_prob": selected_prob,
            "top_logprobs": top_items
        })

    validate_next_word(response_text, token_probs)
    return response_text, token_probs


def validate_next_word(response_text: str, token_probs: List[Dict]) -> None:
    """Reject output that cannot be displayed as one faithful lexical word."""
    raw_tokens = "".join(token["selected_token"] for token in token_probs)
    word = response_text[1:] if response_text.startswith(" ") else response_text

    if (
        raw_tokens != response_text
        or not word
        or response_text != response_text.rstrip()
        or response_text.startswith(("\n", "\t"))
        or not WORD_PATTERN.fullmatch(word)
    ):
        raise RuntimeError("OpenAI did not return a valid next word.")


def get_generation_settings(data: Dict) -> Tuple[int, float]:
    try:
        top_k = int(data.get("top_k", 5))
        temperature = float(data.get("temperature", 0.0))
    except (TypeError, ValueError) as error:
        raise ValueError("Generation settings must be numeric.") from error

    if not 0 <= top_k <= 20:
        raise ValueError("top_k must be between 0 and 20.")
    if not 0 <= temperature <= 2:
        raise ValueError("temperature must be between 0 and 2.")

    return top_k, temperature

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({'error': 'Request body must be a JSON object'}), 400

        prompt = data.get('prompt', '')
        top_k, temperature = get_generation_settings(data)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
            
        response_text, token_probs = get_model_response(prompt, top_k, temperature)
        
        return jsonify({
            'text': response_text,
            'tokenProbs': token_probs
        })
        
    except ValueError as error:
        return jsonify({'error': str(error)}), 400
    except RuntimeError as error:
        return jsonify({'error': str(error)}), 500
    except Exception:
        return jsonify({'error': 'OpenAI generation request failed.'}), 502

if __name__ == '__main__':
    app.run(debug=True, port=5000)
