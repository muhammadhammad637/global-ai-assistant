"""Read-only Instagram Professional account OAuth and insights helpers."""

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid


SCOPES = "instagram_business_basic,instagram_business_manage_insights"


def graph_api_version():
    version = os.environ.get("INSTAGRAM_GRAPH_API_VERSION", "v27.0").strip()
    if not re.fullmatch(r"v\d+\.\d+", version):
        raise ValueError("INSTAGRAM_GRAPH_API_VERSION must look like v27.0.")
    return version


def authorization_url(client_id, redirect_uri, state):
    query = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
        "enable_fb_login": "false",
    })
    return f"https://www.instagram.com/oauth/authorize?{query}"


def _request_json(url, data=None):
    body = None
    headers = {"Accept": "application/json"}
    if data is not None:
        boundary = f"----GlobalAssistant{uuid.uuid4().hex}"
        parts = []
        for name, value in data.items():
            parts.extend((
                f"--{boundary}\r\n".encode("ascii"),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("ascii"),
                str(value).encode("utf-8"),
                b"\r\n",
            ))
        parts.append(f"--{boundary}--\r\n".encode("ascii"))
        body = b"".join(parts)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    request = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.loads(response.read(1_000_000).decode("utf-8"))
    except urllib.error.HTTPError as error:
        try:
            payload = json.loads(error.read(4096).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            payload = {}
        api_error = payload.get("error")
        if isinstance(api_error, dict):
            api_error = api_error.get("message")
        detail = payload.get("error_message") or payload.get("message") or api_error or "request rejected"
        raise RuntimeError(f"Instagram returned HTTP {error.code}: {detail}") from error
    except (urllib.error.URLError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Instagram request failed: {error}") from error
    if not isinstance(result, dict):
        raise RuntimeError("Instagram returned an invalid response.")
    return result


def exchange_code(code, client_id, client_secret, redirect_uri):
    short_token_response = _request_json(
        "https://api.instagram.com/oauth/access_token",
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": code,
        },
    )
    short_token = short_token_response.get("access_token")
    if not isinstance(short_token, str) or not short_token:
        data = short_token_response.get("data")
        if isinstance(data, list) and data and isinstance(data[0], dict):
            short_token = data[0].get("access_token")
    if not isinstance(short_token, str) or not short_token:
        raise RuntimeError("Instagram did not return an access token.")

    version = graph_api_version()
    query = urllib.parse.urlencode({
        "grant_type": "ig_exchange_token",
        "client_secret": client_secret,
        "access_token": short_token,
    })
    long_token_response = _request_json(
        f"https://graph.instagram.com/{version}/access_token?{query}"
    )
    access_token = long_token_response.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise RuntimeError("Instagram did not return a long-lived access token.")
    return {
        "access_token": access_token,
        "expires_in": long_token_response.get("expires_in"),
    }


def account_insights(access_token):
    version = graph_api_version()
    profile_query = urllib.parse.urlencode({
        "fields": "user_id,username,account_type,followers_count,follows_count,media_count",
        "access_token": access_token,
    })
    profile = _request_json(
        f"https://graph.instagram.com/{version}/me?{profile_query}"
    )
    account_id = profile.get("user_id") or profile.get("id")
    if not isinstance(account_id, (str, int)) or not str(account_id):
        raise RuntimeError("Instagram did not return a professional account ID.")

    insights_query = urllib.parse.urlencode({
        "metric": "reach,accounts_engaged,total_interactions",
        "period": "day",
        "metric_type": "total_value",
        "access_token": access_token,
    })
    insights = _request_json(
        f"https://graph.instagram.com/{version}/{account_id}/insights?{insights_query}"
    )
    data = insights.get("data")
    if not isinstance(data, list):
        raise RuntimeError("Instagram returned an invalid insights response.")
    return profile, data
