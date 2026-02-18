# All-in-one
1人團隊

## Twitter/X Asset Monitor

Monitor specific Twitter/X accounts organized by asset sector (semiconductor, gold, silver, etc.) and receive real-time notifications with AI sentiment analysis when they post new content.

### Features

- **Sector-based account organization** - Group Twitter accounts by asset class (semiconductor, gold, silver, crypto, macro, etc.)
- **Multiple scraping backends** - Scweet/GraphQL (recommended), Nitter RSS, or Twitter API v2
- **FinTwitBERT sentiment analysis** - Auto-classify tweets as Bullish/Neutral/Bearish (80% accuracy on financial tweets)
- **Priority-based polling** - High/medium/low priority accounts checked at different intervals
- **Multi-channel notifications** - Console, Telegram, Discord, LINE Notify (all with sentiment badges)
- **Local tweet storage** - SQLite database for history and deduplication
- **CLI interface** - Monitor, check, sentiment, accounts, history, stats

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up X account cookies for Scweet (see "Cookie Setup" below)
cp config/cookies.json.example config/cookies.json
# Edit with your auth_token and ct0 values

# 3. Configure your accounts
vim config/accounts.yaml

# 4. (Optional) Enable sentiment analysis
pip install transformers torch

# 5. (Optional) Set up notification channels
cp .env.example .env
vim .env

# 6. Run it
python main.py accounts           # List configured accounts
python main.py check -u kingkong9888  # Check a single account
python main.py sentiment -t "Gold is breaking out, $2800 incoming" # Test sentiment
python main.py monitor            # Start live monitoring
```

### Cookie Setup (Required for Scweet)

Scweet uses X's internal GraphQL API and needs your browser cookies:

1. Log in to [x.com](https://x.com) in your browser
2. Open DevTools (F12) > Application > Cookies > `https://x.com`
3. Copy the values of `auth_token` and `ct0`
4. Create `config/cookies.json`:

```json
{
    "auth_token": "paste_your_auth_token_here",
    "ct0": "paste_your_ct0_here"
}
```

> **Note:** Cookies expire periodically. If scraping stops working, refresh your cookies.

### Project Structure

```
All-in-one/
├── main.py                    # Entry point
├── config/
│   ├── accounts.yaml          # Twitter accounts grouped by sector
│   ├── settings.yaml          # Global settings (scraper, schedule, notifications)
│   └── cookies.json.example   # Template for X account cookies
├── src/
│   ├── cli.py                 # CLI commands
│   ├── config_loader.py       # YAML config loader with env var override
│   ├── factory.py             # Component factory (scraper, notifiers)
│   ├── sentiment.py           # FinTwitBERT sentiment analysis
│   ├── models/
│   │   ├── account.py         # Account & Sector data models
│   │   ├── database.py        # SQLite storage layer
│   │   └── tweet.py           # Tweet data model
│   ├── scrapers/
│   │   ├── base.py            # Scraper interface
│   │   ├── scweet.py          # Scweet / X GraphQL scraper (recommended)
│   │   ├── nitter.py          # Nitter RSS scraper (fallback)
│   │   └── twitter_api.py     # Twitter API v2 scraper (paid)
│   ├── monitor/
│   │   ├── engine.py          # Core monitoring engine + sentiment
│   │   └── scheduler.py       # Priority-based polling scheduler
│   └── notifiers/
│       ├── base.py            # Notifier interface
│       ├── console.py         # Terminal output (rich) with sentiment badges
│       ├── telegram.py        # Telegram Bot API
│       ├── discord.py         # Discord webhooks
│       └── line_notify.py     # LINE Notify
├── data/                      # SQLite DB & logs (gitignored)
├── requirements.txt
└── .env.example
```

### Sentiment Analysis (FinTwitBERT)

Uses [StephanAkkerman/FinTwitBERT-sentiment](https://huggingface.co/StephanAkkerman/FinTwitBERT-sentiment) - a BERT model pre-trained on 10M+ financial tweets. Handles slang, emojis, cashtags, and crypto/stock jargon.

```bash
# Install (optional, ~500MB model download on first use)
pip install transformers torch

# Analyze any text
python main.py sentiment -t "NVDA earnings crushing it, semis mooning 🚀"
# Output: 🟢 Bullish (92%)

python main.py sentiment -t "Gold dumping hard, support broken at 2600"
# Output: 🔴 Bearish (87%)

# Analyze stored tweets from database
python main.py sentiment -u kingkong9888 -n 20
python main.py sentiment -s gold -n 15
```

When enabled in `config/settings.yaml`, sentiment badges are automatically added to all notifications:
- 🟢 **Bullish** - Positive market signal
- 🔴 **Bearish** - Negative market signal
- ⚪ **Neutral** - Informational/no clear direction

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

### CLI Commands

| Command                            | Description                            |
|------------------------------------|----------------------------------------|
| `python main.py monitor`           | Start live monitoring daemon           |
| `python main.py check -u X`       | Manually check a single account        |
| `python main.py sentiment -t "…"` | Analyze sentiment of any text          |
| `python main.py sentiment -u X`   | Analyze stored tweets from an account  |
| `python main.py sentiment -s gold`| Analyze stored tweets from a sector    |
| `python main.py accounts`          | List all configured accounts/sectors   |
| `python main.py history`           | View stored tweet history              |
| `python main.py stats`             | Show monitoring statistics             |

### Scraper Backends

| Backend | Cost | Setup | Reliability | Status (2026) |
|---------|------|-------|-------------|---------------|
| **Scweet** (default) | Free | X account cookies | High | Actively maintained |
| **Twitter API v2** | $100/mo+ | Bearer Token | High | Official but expensive |
| **Nitter RSS** | Free | None | Low | Most instances dead |

Switch backend in `config/settings.yaml`:
```yaml
scraper:
  backend: "scweet"   # or "api" or "nitter"
```
