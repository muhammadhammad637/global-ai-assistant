"""Provider helpers shared by the Streamlit app and mobile API."""

import json
import urllib.error
import urllib.parse
import urllib.request


def generate_speech(text, api_key, language):
    payload = json.dumps({
        "model": "gpt-4o-mini-tts",
        "voice": "alloy",
        "input": text[:4000],
        "instructions": f"Speak clearly and naturally in language code {language}.",
        "response_format": "mp3",
    }).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            audio = response.read(12_000_000)
        if not audio.startswith(b"ID3") and not audio.startswith(b"\xff\xfb"):
            raise ValueError("The speech provider returned an unsupported audio response.")
        return audio
    except urllib.error.HTTPError as error:
        detail = error.read(2048).decode("utf-8", errors="replace")
        raise RuntimeError(f"Speech provider returned HTTP {error.code}: {detail}") from error
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        raise RuntimeError(f"Speech generation failed: {error}") from error


def runway_request(path, api_key, payload=None):
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        f"https://api.dev.runwayml.com{path}",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "X-Runway-Version": "2024-11-06",
            "Content-Type": "application/json",
        },
        method="POST" if body is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read(2048).decode("utf-8", errors="replace")
        raise RuntimeError(f"Runway returned HTTP {error.code}: {detail}") from error
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Runway request failed: {error}") from error


def start_runway_video(prompt, api_key):
    if not prompt.strip():
        raise ValueError("Enter a video description first.")
    if len(prompt) > 1000:
        raise ValueError("Video descriptions must be 1,000 characters or fewer.")
    task = runway_request(
        "/v1/text_to_video",
        api_key,
        {"model": "gen4.5", "promptText": prompt.strip()},
    )
    task_id = task.get("id")
    if not isinstance(task_id, str) or not task_id:
        raise RuntimeError("Runway did not return a task ID.")
    return task_id


def get_runway_video(task_id, api_key):
    return runway_request(
        f"/v1/tasks/{urllib.parse.quote(task_id, safe='')}",
        api_key,
    )
