# All-in-one Content Distribution Workflow

1人團隊 — One-person content pipeline: read local articles → summarise in your voice → publish everywhere.

## How It Works

```
content_input/          (your PDFs, DOCX, TXT, MD, HTML files)
       │
       ▼
  ┌──────────┐     ┌───────────────────┐
  │  Reader   │────▶│  Summariser (LLM) │◀── writing style from Notion
  └──────────┘     └────────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼              ▼
        Notion DB      Telegram       Patreon       YouTube
        (full summary) (short post)   (teaser)      (community post)
```

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys (see setup guides below)
```

### 3. Add your content

Drop PDFs, DOCX, TXT, MD, or HTML files into the `content_input/` folder.

### 4. Run the pipeline

```bash
python run.py                     # full pipeline
python run.py --dry-run           # test without calling APIs
python run.py --skip-patreon      # skip specific platforms
python run.py -i /path/to/folder  # use a different input directory
```

## API Setup Guides

### Notion (required)

1. Go to [Notion Integrations](https://www.notion.so/my-integrations) and create an integration.
2. Copy the **Internal Integration Token** → `NOTION_API_KEY` in `.env`.
3. Create a database in Notion for your summaries (at minimum it needs a **Name** title property).
4. Share the database with your integration (click "..." → "Add connections").
5. Copy the database ID from the URL → `NOTION_DATABASE_ID` in `.env`.
   - URL format: `https://notion.so/<workspace>/<DATABASE_ID>?v=...`

The workflow will automatically read your recent pages to learn your writing style.

### Telegram (required)

1. Message [@BotFather](https://t.me/BotFather) on Telegram and create a new bot.
2. Copy the bot token → `TELEGRAM_BOT_TOKEN` in `.env`.
3. Add the bot to your channel/group as an admin.
4. Get your chat ID:
   - For channels: forward a message from the channel to [@userinfobot](https://t.me/userinfobot).
   - Or use: `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Set `TELEGRAM_CHAT_ID` in `.env` (prefix channels with `-100`).

### OpenAI / LLM (required for summarisation)

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys).
2. Set `OPENAI_API_KEY` in `.env`.
3. Optionally change the model: `OPENAI_MODEL=gpt-4o`
4. For local LLMs, set `OPENAI_BASE_URL` to your compatible endpoint.

### Patreon (optional)

1. Go to the [Patreon Developer Portal](https://www.patreon.com/portal/registration/register-clients).
2. Create an API client and copy the **Creator's Access Token** → `PATREON_ACCESS_TOKEN`.
3. Find your Campaign ID:
   ```bash
   curl -H "Authorization: Bearer <TOKEN>" \
        https://www.patreon.com/api/oauth2/v2/campaigns
   ```
4. Set `PATREON_CAMPAIGN_ID` in `.env`.

### YouTube Community Posts (optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. Enable the **YouTube Data API v3**.
3. Create **OAuth 2.0 credentials** (Desktop application).
4. Download the JSON file → save as `client_secrets.json` in the project root.
5. Set `YOUTUBE_CHANNEL_ID` in `.env`.
6. On first run a browser window will open for OAuth consent.

## CLI Options

| Flag              | Description                          |
|-------------------|--------------------------------------|
| `-i`, `--input-dir` | Path to articles directory          |
| `--skip-notion`   | Skip Notion database save            |
| `--skip-telegram` | Skip Telegram post                   |
| `--skip-patreon`  | Skip Patreon post                    |
| `--skip-youtube`  | Skip YouTube community post          |
| `--dry-run`       | Run without calling any external API |

## Project Structure

```
All-in-one/
├── run.py                  # CLI entrypoint
├── requirements.txt
├── .env.example            # Template — copy to .env
├── content_input/          # Drop articles here
│   └── .gitkeep
└── workflow/
    ├── config.py           # Loads .env settings
    ├── reader.py           # Reads PDF/DOCX/TXT/MD/HTML
    ├── notion_client.py    # Read style + write summaries
    ├── summariser.py       # LLM-powered summarisation
    ├── pipeline.py         # Orchestrator
    └── distributors/
        ├── telegram.py     # Telegram Bot API
        ├── patreon.py      # Patreon API v2
        └── youtube.py      # YouTube Data API v3
```
