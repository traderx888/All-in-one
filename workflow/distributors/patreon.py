"""Publish posts to Patreon via their API v2.

Setup guide
-----------
1. Go to https://www.patreon.com/portal/registration/register-clients
2. Create a new API client (or use an existing one).
3. Copy your **Creator's Access Token** from the client page.
4. Find your **Campaign ID**:
       curl -H "Authorization: Bearer <TOKEN>" \
            https://www.patreon.com/api/oauth2/v2/campaigns
5. Add both values to your .env file:
       PATREON_ACCESS_TOKEN=...
       PATREON_CAMPAIGN_ID=...
"""

from __future__ import annotations
import requests
from workflow import config

_API_BASE = "https://www.patreon.com/api/oauth2/v2"


def send_post(title: str, body: str, is_public: bool = False) -> dict:
    """Create a new text post on Patreon.

    Parameters
    ----------
    title : str
        Post title shown to patrons.
    body : str
        Post body (plain text or simple HTML).
    is_public : bool
        If True the post is visible to everyone, otherwise patrons-only.
    """
    if not config.PATREON_ACCESS_TOKEN or not config.PATREON_CAMPAIGN_ID:
        raise RuntimeError(
            "PATREON_ACCESS_TOKEN and PATREON_CAMPAIGN_ID must be set in .env. "
            "See the docstring in this module for a setup guide."
        )

    headers = {
        "Authorization": f"Bearer {config.PATREON_ACCESS_TOKEN}",
        "Content-Type": "application/vnd.api+json",
    }

    payload = {
        "data": {
            "type": "post",
            "attributes": {
                "title": title,
                "content": body,
                "is_paid": not is_public,
                "is_public": is_public,
            },
            "relationships": {
                "campaign": {
                    "data": {
                        "type": "campaign",
                        "id": config.PATREON_CAMPAIGN_ID,
                    }
                }
            },
        }
    }

    resp = requests.post(
        f"{_API_BASE}/posts",
        json=payload,
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
