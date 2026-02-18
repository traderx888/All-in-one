"""CLI interface for the Twitter/X Asset Monitor."""

import asyncio
import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

from src.config_loader import load_settings, load_accounts
from src.models.database import Database
from src.factory import create_scraper, create_notifiers
from src.monitor.engine import MonitorEngine
from src.monitor.scheduler import MonitorScheduler

console = Console()


def setup_logging(level: str = "INFO", log_file: str = ""):
    """Configure logging with rich handler."""
    handlers = [RichHandler(console=console, show_path=False, markup=True)]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        handlers=handlers,
    )


@click.group()
@click.option("--config", default=None, help="Path to settings.yaml")
@click.pass_context
def cli(ctx, config):
    """Twitter/X Asset Monitor - Track sector-specific accounts."""
    ctx.ensure_object(dict)
    ctx.obj["settings_path"] = config


@cli.command()
@click.pass_context
def monitor(ctx):
    """Start the live monitoring daemon."""
    settings = load_settings(ctx.obj.get("settings_path"))
    log_cfg = settings.get("logging", {})
    setup_logging(log_cfg.get("level", "INFO"), log_cfg.get("file", ""))

    sectors, all_accounts = load_accounts()
    if not all_accounts:
        console.print("[red]No accounts configured. Edit config/accounts.yaml[/red]")
        sys.exit(1)

    db = Database(settings.get("database", {}).get("path", "data/tweets.db"))
    scraper = create_scraper(settings)
    notifiers = create_notifiers(settings)
    engine = MonitorEngine(scraper, db, notifiers)

    schedule_cfg = settings.get("schedule", {})
    scheduler = MonitorScheduler(
        engine=engine,
        accounts=all_accounts,
        high_interval=schedule_cfg.get("high_priority_interval", 120),
        medium_interval=schedule_cfg.get("medium_priority_interval", 300),
        low_interval=schedule_cfg.get("low_priority_interval", 900),
    )

    console.print(
        f"[bold green]Starting monitor[/bold green] - "
        f"{len(all_accounts)} accounts across {len(sectors)} sectors"
    )
    console.print("Press Ctrl+C to stop.\n")

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(scheduler.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
        loop.run_until_complete(scheduler.stop())
    finally:
        loop.close()


@cli.command()
@click.option("--username", "-u", default=None, help="Filter by @username")
@click.option("--sector", "-s", default=None, help="Filter by sector name")
@click.option("--limit", "-n", default=20, help="Number of tweets to show")
@click.pass_context
def history(ctx, username, sector, limit):
    """View stored tweet history."""
    settings = load_settings(ctx.obj.get("settings_path"))
    db = Database(settings.get("database", {}).get("path", "data/tweets.db"))

    tweets = db.get_recent_tweets(username=username, sector=sector, limit=limit)
    if not tweets:
        console.print("[dim]No tweets found.[/dim]")
        return

    table = Table(title="Tweet History", show_lines=True)
    table.add_column("Time", style="dim", width=16)
    table.add_column("Sector", style="bold")
    table.add_column("Account", style="cyan")
    table.add_column("Tweet", max_width=60)
    table.add_column("Link", style="dim")

    for t in tweets:
        table.add_row(
            t["created_at"][:16],
            t.get("sector", ""),
            f"@{t['username']}",
            t["text"][:100] + ("..." if len(t["text"]) > 100 else ""),
            t.get("url", ""),
        )

    console.print(table)
    db.close()


@cli.command()
@click.pass_context
def accounts(ctx):
    """List all monitored accounts and their sectors."""
    sectors, all_accounts = load_accounts()

    table = Table(title="Monitored Accounts", show_lines=True)
    table.add_column("Username", style="cyan bold")
    table.add_column("Sectors", style="yellow")
    table.add_column("Priority", style="bold")
    table.add_column("Note", style="dim")

    for account in sorted(all_accounts.values(), key=lambda a: a.username):
        pri_style = {
            "high": "red bold",
            "medium": "yellow",
            "low": "dim",
        }.get(account.priority, "")

        table.add_row(
            f"@{account.username}",
            ", ".join(account.sectors),
            f"[{pri_style}]{account.priority}[/{pri_style}]",
            account.note,
        )

    console.print(table)

    # Also show sector summary
    console.print()
    sector_table = Table(title="Sectors", show_lines=True)
    sector_table.add_column("Sector", style="bold")
    sector_table.add_column("Description")
    sector_table.add_column("Accounts", style="cyan")

    for sector in sectors:
        sector_table.add_row(
            sector.name,
            sector.description,
            ", ".join(f"@{a.username}" for a in sector.accounts),
        )

    console.print(sector_table)


@cli.command()
@click.option("--username", "-u", required=True, help="Twitter handle to check")
@click.pass_context
def check(ctx, username):
    """Manually check a single account for new tweets."""
    settings = load_settings(ctx.obj.get("settings_path"))
    log_cfg = settings.get("logging", {})
    setup_logging(log_cfg.get("level", "INFO"), log_cfg.get("file", ""))

    # Remove @ prefix if present
    username = username.lstrip("@")

    from src.models.account import Account

    db = Database(settings.get("database", {}).get("path", "data/tweets.db"))
    scraper = create_scraper(settings)
    notifiers = create_notifiers(settings)
    engine = MonitorEngine(scraper, db, notifiers)
    account = Account(username=username, priority="high", sectors=["manual_check"])

    console.print(f"Checking @{username}...")

    loop = asyncio.new_event_loop()
    try:
        new_tweets = loop.run_until_complete(engine.check_account(account))
        if new_tweets:
            console.print(
                f"\n[green]Found {len(new_tweets)} new tweet(s) from @{username}[/green]"
            )
        else:
            console.print(f"\n[dim]No new tweets from @{username}[/dim]")
    finally:
        loop.run_until_complete(engine.close())
        loop.close()


@cli.command()
@click.pass_context
def stats(ctx):
    """Show monitoring statistics."""
    settings = load_settings(ctx.obj.get("settings_path"))
    db = Database(settings.get("database", {}).get("path", "data/tweets.db"))

    account_stats = db.get_account_stats()
    if not account_stats:
        console.print("[dim]No data collected yet. Run 'monitor' first.[/dim]")
        db.close()
        return

    table = Table(title="Monitoring Statistics")
    table.add_column("Account", style="cyan")
    table.add_column("Tweets Stored", justify="right")
    table.add_column("Latest Tweet", style="dim")
    table.add_column("Last Fetched", style="dim")

    for s in account_stats:
        table.add_row(
            f"@{s['username']}",
            str(s["tweet_count"]),
            (s["latest_tweet"] or "")[:16],
            (s["last_fetch_at"] or "")[:16],
        )

    console.print(table)
    db.close()


if __name__ == "__main__":
    cli()
