# All-in-one
1人團隊

## Polymarket Oil Price Alert Bot

Monitors [Polymarket](https://polymarket.com) prediction markets for oil-related votes and sends real-time alerts to Telegram when:

- A **new oil-related market** appears
- An existing market has a **significant price change** (configurable threshold)

### Quick Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a Telegram bot**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` and follow the prompts
   - Copy the bot token

3. **Get your Chat ID**
   - Message [@userinfobot](https://t.me/userinfobot) on Telegram
   - It will reply with your chat ID

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your bot token and chat ID
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

### Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | — | Your Telegram bot token from BotFather |
| `TELEGRAM_CHAT_ID` | — | Your Telegram chat ID |
| `POLL_INTERVAL` | `300` | How often to check Polymarket (seconds) |
| `OIL_KEYWORDS` | `oil,crude,brent,wti,petroleum,opec` | Keywords to match markets |
| `PRICE_CHANGE_THRESHOLD` | `5` | Min price change (%) to trigger alert |

### Architecture

```
bot.py                  — Main loop: poll → compare → alert
polymarket_client.py    — Fetches & filters markets from Polymarket Gamma API
telegram_alert.py       — Formats & sends Telegram messages
market_state.json       — Persisted state (auto-generated, gitignored)
```
