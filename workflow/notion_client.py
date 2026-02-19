"""Notion integration — read writing style & save summaries to a database."""

from __future__ import annotations
from notion_client import Client
from workflow import config


def _client() -> Client:
    return Client(auth=config.NOTION_API_KEY)


# ---------------------------------------------------------------------------
# Read existing pages to learn writing style
# ---------------------------------------------------------------------------

def _extract_text_from_blocks(blocks: list[dict]) -> str:
    """Recursively extract plain text from Notion block objects."""
    parts: list[str] = []
    for block in blocks:
        btype = block.get("type", "")
        content = block.get(btype, {})

        # Most text-bearing blocks store text in "rich_text"
        rich_text = content.get("rich_text", [])
        if rich_text:
            line = "".join(rt.get("plain_text", "") for rt in rich_text)
            parts.append(line)

        # Handle child blocks if present
        if block.get("has_children"):
            try:
                children = _client().blocks.children.list(block_id=block["id"])
                parts.append(_extract_text_from_blocks(children.get("results", [])))
            except Exception:
                pass

    return "\n".join(parts)


def _page_ids_from_database(limit: int = 5) -> list[str]:
    """Return the most recent page IDs from the configured database."""
    resp = _client().databases.query(
        database_id=config.NOTION_DATABASE_ID,
        page_size=limit,
        sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
    )
    return [page["id"] for page in resp.get("results", [])]


def read_writing_samples(max_pages: int = 5) -> str:
    """Return concatenated text from recent Notion pages to use as style reference."""
    page_ids = config.NOTION_STYLE_PAGE_IDS or _page_ids_from_database(max_pages)

    samples: list[str] = []
    for pid in page_ids[:max_pages]:
        try:
            blocks = _client().blocks.children.list(block_id=pid)
            text = _extract_text_from_blocks(blocks.get("results", []))
            if text.strip():
                samples.append(text.strip())
        except Exception as exc:
            print(f"  [warning] Could not read page {pid}: {exc}")

    return "\n\n---\n\n".join(samples)


# ---------------------------------------------------------------------------
# Write summary to database
# ---------------------------------------------------------------------------

def save_summary(
    title: str,
    summary: str,
    source: str = "",
    tags: list[str] | None = None,
) -> str:
    """Create a new page in the Notion database and return its URL."""
    tags = tags or []

    # Build the page properties — adapts to common database schemas
    properties: dict = {
        "Name": {"title": [{"text": {"content": title}}]},
    }

    # Attempt to add optional properties (they'll silently fail if the
    # database schema doesn't include them).
    if source:
        properties["Source"] = {"url": source}
    if tags:
        properties["Tags"] = {
            "multi_select": [{"name": t} for t in tags],
        }

    # Body as block children
    children = _markdown_to_blocks(summary)

    try:
        page = _client().pages.create(
            parent={"database_id": config.NOTION_DATABASE_ID},
            properties=properties,
            children=children,
        )
        return page.get("url", page["id"])
    except Exception as exc:
        # If properties fail, retry with title-only
        print(f"  [info] Retrying with minimal properties: {exc}")
        page = _client().pages.create(
            parent={"database_id": config.NOTION_DATABASE_ID},
            properties={"Name": {"title": [{"text": {"content": title}}]}},
            children=children,
        )
        return page.get("url", page["id"])


def _markdown_to_blocks(text: str) -> list[dict]:
    """Convert plain / markdown text into Notion block objects."""
    blocks: list[dict] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("# "):
            blocks.append(_heading_block(stripped[2:], level=1))
        elif stripped.startswith("## "):
            blocks.append(_heading_block(stripped[3:], level=2))
        elif stripped.startswith("### "):
            blocks.append(_heading_block(stripped[4:], level=3))
        elif stripped.startswith(("- ", "* ")):
            blocks.append(_bulleted_list_block(stripped[2:]))
        else:
            blocks.append(_paragraph_block(stripped))
    return blocks


def _paragraph_block(text: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _heading_block(text: str, level: int = 2) -> dict:
    htype = f"heading_{level}"
    return {
        "object": "block",
        "type": htype,
        htype: {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _bulleted_list_block(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }
