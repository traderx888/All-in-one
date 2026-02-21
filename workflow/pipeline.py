"""Main orchestration pipeline — ties every module together."""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

from workflow import config
from workflow.reader import load_articles, Article
from workflow.notion_client import read_writing_samples, save_summary
from workflow.summariser import summarise, make_short_post
from workflow.distributors import telegram as tg_dist
from workflow.distributors import patreon as pat_dist
from workflow.distributors import youtube as yt_dist


def run(
    input_dir: Path | None = None,
    skip_notion: bool = False,
    skip_telegram: bool = False,
    skip_patreon: bool = False,
    skip_youtube: bool = False,
    dry_run: bool = False,
) -> None:
    input_dir = input_dir or config.CONTENT_INPUT_DIR

    # ── 1. Load articles ────────────────────────────────────────
    print(f"\n📂  Scanning {input_dir} for articles …")
    articles = load_articles(input_dir)
    if not articles:
        print("   No supported files found. Add PDFs, DOCX, TXT, MD, or HTML files "
              f"to {input_dir} and re-run.")
        sys.exit(1)
    print(f"   Found {len(articles)} article(s).\n")

    # ── 2. Read writing style from Notion ───────────────────────
    print("✍️   Reading your writing style from Notion …")
    style_samples = ""
    try:
        style_samples = read_writing_samples()
        if style_samples:
            word_count = len(style_samples.split())
            print(f"   Loaded {word_count} words of style reference.\n")
        else:
            print("   No existing pages found — will use a neutral style.\n")
    except Exception as exc:
        print(f"   Could not read Notion pages ({exc}). Proceeding with neutral style.\n")

    # ── 3. Process each article ─────────────────────────────────
    for i, article in enumerate(articles, 1):
        print(f"{'─' * 60}")
        print(f"📄  [{i}/{len(articles)}] {article.title}")
        print(f"    Source: {article.source_path}")

        # Summarise
        print("    Summarising …")
        if dry_run:
            summary = f"[DRY RUN] Summary of: {article.title}"
        else:
            summary = summarise(article.title, article.body, style_samples)
        print(f"    Summary: {len(summary)} chars\n")

        # ── 3a. Save to Notion database ─────────────────────────
        if not skip_notion:
            print("    → Saving to Notion …", end=" ")
            if dry_run:
                print("[DRY RUN]")
            else:
                try:
                    url = save_summary(
                        title=article.title,
                        summary=summary,
                        source=article.source_path,
                    )
                    print(f"✓  {url}")
                except Exception as exc:
                    print(f"✗  {exc}")

        # ── 3b. Distribute to Telegram ──────────────────────────
        if not skip_telegram:
            print("    → Sending to Telegram …", end=" ")
            if dry_run:
                print("[DRY RUN]")
            else:
                try:
                    tg_post = make_short_post(summary, platform="telegram")
                    tg_dist.send_post(tg_post)
                    print("✓")
                except Exception as exc:
                    print(f"✗  {exc}")

        # ── 3c. Distribute to Patreon ───────────────────────────
        if not skip_patreon:
            print("    → Posting to Patreon …", end=" ")
            if dry_run:
                print("[DRY RUN]")
            else:
                try:
                    pat_post = make_short_post(summary, platform="patreon")
                    pat_dist.send_post(title=article.title, body=pat_post)
                    print("✓")
                except Exception as exc:
                    print(f"✗  {exc}")

        # ── 3d. Post to YouTube community ───────────────────────
        if not skip_youtube:
            print("    → Posting to YouTube …", end=" ")
            if dry_run:
                print("[DRY RUN]")
            else:
                try:
                    yt_post = make_short_post(summary, platform="youtube")
                    result = yt_dist.send_community_post(yt_post)
                    if isinstance(result, dict):
                        print("✓")
                    else:
                        print("⚠  fallback (see output above)")
                except Exception as exc:
                    print(f"✗  {exc}")

        print()

    print(f"{'─' * 60}")
    print("✅  Pipeline complete.\n")


# ── CLI ─────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Content Distribution Workflow — summarise articles and distribute everywhere.",
    )
    parser.add_argument(
        "-i", "--input-dir",
        type=Path,
        default=None,
        help=f"Directory containing articles (default: {config.CONTENT_INPUT_DIR})",
    )
    parser.add_argument("--skip-notion", action="store_true", help="Skip saving to Notion")
    parser.add_argument("--skip-telegram", action="store_true", help="Skip Telegram distribution")
    parser.add_argument("--skip-patreon", action="store_true", help="Skip Patreon distribution")
    parser.add_argument("--skip-youtube", action="store_true", help="Skip YouTube distribution")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the pipeline without calling any APIs (useful for testing)",
    )

    args = parser.parse_args()
    run(
        input_dir=args.input_dir,
        skip_notion=args.skip_notion,
        skip_telegram=args.skip_telegram,
        skip_patreon=args.skip_patreon,
        skip_youtube=args.skip_youtube,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
