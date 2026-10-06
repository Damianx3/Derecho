import json
import urllib.request
import urllib.error


GEMMA_URL = "http://127.0.0.1:9379/v1/chat/completions"
MODEL_NAME = "gemma4-e2b"


def translate_text(
    text: str,
    source_language: str,
    target_language: str,
) -> str:
    """Translate text using the local Gemma LiteRT-LM server."""

    system_prompt = (
        f"Translate {source_language} to {target_language}. "
        "Return only the translation."
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    }

    # Convert the Python dictionary into JSON bytes for HTTP.
    data = json.dumps(payload).encode("utf-8")

    # Create the HTTP POST request.
    request = urllib.request.Request(
        GEMMA_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        # Send the request to the local Gemma server.
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8")
        raise RuntimeError(
            f"Gemma returned HTTP {error.code}: {error_body}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Could not connect to Gemma at {GEMMA_URL}: {error}"
        ) from error

    result = json.loads(response_body)

    # Extract only the translated sentence.
    translation = result["choices"][0]["message"]["content"]

    return translation.strip()


if __name__ == "__main__":
    translation = translate_text(
        "¿Dónde está el hospital más cercano?",
        "Spanish",
        "English",
    )

    print("Translation:", translation)
