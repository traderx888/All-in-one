"""Summarise articles using an OpenAI-compatible LLM, adopting the user's writing style."""

from __future__ import annotations
from openai import OpenAI
from workflow import config

_SYSTEM_PROMPT = """\
You are a content writer assistant.  Your job is to read a raw article or
report and produce a polished summary **in the exact same tone, vocabulary,
and structure** as the STYLE REFERENCE below.

STYLE REFERENCE (the user's own writing):
\"\"\"
{style_samples}
\"\"\"

Rules:
1. Keep the summary concise — aim for 300-600 words unless the source is very long.
2. Preserve the author's voice: sentence length, paragraph style, emoji usage (or lack thereof), level of formality.
3. Use markdown formatting (headings, bullets, bold) where the style reference does.
4. End with a short, punchy takeaway or call-to-action if the style reference tends to do so.
5. Do NOT fabricate facts — only use information from the source article.
"""

_USER_PROMPT = """\
Summarise the following article/report.

TITLE: {title}

CONTENT:
{content}
"""


def summarise(
    title: str,
    content: str,
    style_samples: str,
    max_content_chars: int = 60_000,
) -> str:
    """Return a summary string written in the user's style."""
    client = OpenAI(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
    )

    # Truncate very long articles to fit context window
    if len(content) > max_content_chars:
        content = content[:max_content_chars] + "\n\n[…truncated]"

    resp = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": _SYSTEM_PROMPT.format(style_samples=style_samples[:8000]),
            },
            {
                "role": "user",
                "content": _USER_PROMPT.format(title=title, content=content),
            },
        ],
        temperature=0.7,
        max_tokens=2048,
    )
    return resp.choices[0].message.content.strip()


def make_short_post(summary: str, platform: str = "telegram") -> str:
    """Condense a full summary into a short post suitable for social platforms."""
    client = OpenAI(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
    )

    length_hint = {
        "telegram": "Keep it under 1000 characters. Use minimal markdown (bold, links).",
        "youtube": "Keep it under 500 characters. Make it engaging and add relevant hashtags.",
        "patreon": "Keep it under 1500 characters. Make it personal, tease the full version.",
    }

    resp = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You rewrite article summaries into short {platform} posts. "
                    f"{length_hint.get(platform, '')} "
                    "Preserve the author's tone from the summary."
                ),
            },
            {"role": "user", "content": f"Rewrite this summary as a {platform} post:\n\n{summary}"},
        ],
        temperature=0.7,
        max_tokens=512,
    )
    return resp.choices[0].message.content.strip()
