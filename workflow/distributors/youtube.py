"""Post community updates to YouTube via the Data API v3.

Setup guide
-----------
1. Go to https://console.cloud.google.com/ and create a project (or use an existing one).
2. Enable the **YouTube Data API v3**.
3. Create **OAuth 2.0 credentials** (Desktop application type).
4. Download the JSON file and save it as ``client_secrets.json`` in the project root.
5. Set YOUTUBE_CHANNEL_ID in your .env file.
6. The first time you run the workflow, a browser window will open for OAuth consent.

Note: The YouTube Data API community post endpoint has limited availability.
If it is not enabled for your channel, this module falls back to printing the
post content so you can copy-paste it manually.
"""

from __future__ import annotations
import os
from pathlib import Path
from workflow import config

_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def _get_authenticated_service():
    """Build an authenticated YouTube API service."""
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    token_path = Path("token.json")
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), _SCOPES)

    if not creds or not creds.valid:
        secrets_file = config.YOUTUBE_CLIENT_SECRETS_FILE
        if not os.path.exists(secrets_file):
            raise RuntimeError(
                f"YouTube client secrets file not found at '{secrets_file}'. "
                "See the docstring in this module for setup instructions."
            )
        flow = InstalledAppFlow.from_client_secrets_file(secrets_file, _SCOPES)
        creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def send_community_post(text: str) -> dict | str:
    """Attempt to create a YouTube community post.

    Returns the API response dict on success, or a fallback message
    with the text content if the API is unavailable.
    """
    if not config.YOUTUBE_CLIENT_SECRETS_FILE:
        return _fallback(text, reason="YOUTUBE_CLIENT_SECRETS_FILE not set")

    try:
        youtube = _get_authenticated_service()

        # The community post API uses activities.insert (or the newer
        # community post endpoint when available).
        body = {
            "snippet": {
                "channelId": config.YOUTUBE_CHANNEL_ID,
                "description": text,
                "type": "bulletin",
            }
        }

        resp = youtube.activities().insert(part="snippet", body=body).execute()
        return resp
    except Exception as exc:
        return _fallback(text, reason=str(exc))


def _fallback(text: str, reason: str = "") -> str:
    """Return a human-friendly message when automated posting isn't possible."""
    msg = (
        "[YouTube] Automated community post not available"
        f"{f' ({reason})' if reason else ''}.\n"
        "Copy the text below and paste it as a community post on YouTube:\n"
        "─" * 40 + "\n"
        f"{text}\n"
        "─" * 40
    )
    print(msg)
    return msg
