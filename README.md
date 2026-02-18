# All-in-one
1人團隊

## Twitter/X Asset Monitor

Monitor specific Twitter/X accounts organized by asset sector (semiconductor, gold, silver, etc.) and receive real-time notifications when they post new content.

### Features

- **Sector-based account organization** - Group Twitter accounts by asset class (semiconductor, gold, silver, crypto, macro, etc.)
- **Multiple scraping backends** - Nitter RSS (free) or Twitter API v2 (paid)
- **Priority-based polling** - High/medium/low priority accounts checked at different intervals
- **Multi-channel notifications** - Console, Telegram, Discord, LINE Notify
- **Local tweet storage** - SQLite database for history and deduplication
- **CLI interface** - Monitor, check accounts, view history, stats

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your accounts (edit the YAML file)
# Add/remove Twitter handles organized by sector
vim config/accounts.yaml

# (Optional) Set up notification channels
cp .env.example .env
vim .env

# List configured accounts
python main.py accounts

# Manually check a single account
python main.py check -u chipsandwafers

# Start the live monitor daemon
python main.py monitor
```

### Project Structure

```
All-in-one/
├── main.py                    # Entry point
├── config/
│   ├── accounts.yaml          # Twitter accounts grouped by sector
│   └── settings.yaml          # Global settings (scraper, schedule, notifications)
├── src/
│   ├── cli.py                 # CLI commands (monitor, check, history, stats, accounts)
│   ├── config_loader.py       # YAML config loader with env var override
│   ├── factory.py             # Component factory (scraper, notifiers)
│   ├── models/
│   │   ├── account.py         # Account & Sector data models
│   │   ├── database.py        # SQLite storage layer
│   │   └── tweet.py           # Tweet data model
│   ├── scrapers/
│   │   ├── base.py            # Scraper interface
│   │   ├── nitter.py          # Nitter RSS scraper (free, no API key)
│   │   └── twitter_api.py     # Twitter API v2 scraper (paid)
│   ├── monitor/
│   │   ├── engine.py          # Core monitoring engine
│   │   └── scheduler.py       # Priority-based polling scheduler
│   └── notifiers/
│       ├── base.py            # Notifier interface
│       ├── console.py         # Terminal output (rich)
│       ├── telegram.py        # Telegram Bot API
│       ├── discord.py         # Discord webhooks
│       └── line_notify.py     # LINE Notify
├── data/                      # SQLite DB & logs (gitignored)
├── requirements.txt
└── .env.example
```

### Configuration

#### Adding Accounts (`config/accounts.yaml`)

```yaml
sectors:
  semiconductor:
    description: "Semiconductor & memory chip industry"
    accounts:
      - username: "chipsandwafers"
        note: "Semiconductor deep analysis"
        priority: high
      - username: "QQ_Timmy"
        note: "Memory sector insights"
        priority: high

  gold:
    description: "Gold market analysis"
    accounts:
      - username: "kingkong9888"
        priority: high
      - username: "InProved_Metals"
        priority: medium
```

#### Notification Setup

Set environment variables or edit `config/settings.yaml`:

| Channel  | Env Variable          | How to Get                                |
|----------|-----------------------|-------------------------------------------|
| Telegram | `TELEGRAM_BOT_TOKEN`  | Create bot via @BotFather                 |
|          | `TELEGRAM_CHAT_ID`    | Get from @userinfobot                     |
| Discord  | `DISCORD_WEBHOOK_URL` | Server Settings > Integrations > Webhooks |
| LINE     | `LINE_NOTIFY_TOKEN`   | https://notify-bot.line.me/               |

#### Polling Intervals (`config/settings.yaml`)

```yaml
schedule:
  high_priority_interval: 120    # 2 minutes
  medium_priority_interval: 300  # 5 minutes
  low_priority_interval: 900     # 15 minutes
```

### CLI Commands

| Command                     | Description                          |
|-----------------------------|--------------------------------------|
| `python main.py monitor`    | Start live monitoring daemon         |
| `python main.py check -u X` | Manually check a single account      |
| `python main.py accounts`   | List all configured accounts/sectors |
| `python main.py history`    | View stored tweet history            |
| `python main.py stats`      | Show monitoring statistics           |

### Scraper Backends

| Backend | Cost | Setup | Reliability |
|---------|------|-------|-------------|
| **Nitter RSS** (default) | Free | None | Depends on public instances |
| **Twitter API v2** | $100/mo+ | Bearer Token required | High |

Switch backend in `config/settings.yaml`:
```yaml
scraper:
  backend: "nitter"   # or "api"
```
