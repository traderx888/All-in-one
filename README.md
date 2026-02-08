# All-in-One Multi-Agent Trading System

1人團隊 — One-person team, many agents.

## Architecture

```
User (CEO)
├── Secretary (Secy)          — Routes commands, aggregates status
├── Library (Librarian)       — Shared knowledge store
│
└── MANAGEMENT HUB
    ├── Zone LAW
    │   └── ComplianceChecker — Risk validation, position limits
    └── Zone ARD
        ├── SystemPilot       — Agent health monitoring
        ├── TaskManager       — Task routing & lifecycle
        ├── DatabaseChecker   — Data integrity & storage
        └── MasterArchitect   — Config & architecture management
            │
            ├── TRADING DEV
            │   ├── Daytrade Engine    (Researcher → Foreman → Workers)
            │   ├── Auto Trading       (Researcher → Foreman → Workers)
            │   └── Signal Alert       (Researcher → Foreman → Workers)
            │
            ├── PRODUCT DEV
            │   ├── Article_RSS        (Researcher → Foreman → Workers)
            │   ├── PolyMarket         (Researcher → Foreman → Workers)
            │   └── Telegram Bot       (Researcher → Foreman → Workers)
            │
            └── CONTENT DEV
                ├── Content Pilot → TrafficMonitor → DataAnalyst
                ├── Booster Chain: KPI → Campaign
                └── Content Chain: PA → CMD → Generator → ArticleKeeper
```

## Quick Start

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env         # Edit with your API keys

# 4. Run
python -m src.main
# or with custom config:
python -m src.main --config config/settings.yaml
```

## VS Code

Open the project folder in VS Code. Pre-configured launch configurations:
- **Run Trading System** — starts the full agent system
- **Run Tests** — runs pytest suite

## Project Structure

```
src/
├── core/                    # Framework: base agent, messaging, pipeline
│   ├── base_agent.py        # BaseAgent abstract class
│   ├── message.py           # MessageBus & Message types
│   ├── pipeline.py          # Researcher → Foreman → Workers pattern
│   └── agent_registry.py    # Agent discovery & tracking
├── ceo/                     # Secretary + Librarian
├── management_hub/          # ComplianceChecker, SystemPilot, TaskManager...
├── trading_dev/             # Daytrade, Auto Trading, Signal Alert
├── product_dev/             # Article RSS, PolyMarket, Telegram Bot
├── content_dev/             # Content chains & boosters
└── main.py                  # Entry point — builds & runs entire system
```

## Configuration

Edit `config/settings.yaml` to:
- Enable/disable divisions and sub-systems
- Set trading parameters (watchlist, risk limits, timeframes)
- Toggle paper/live trading mode
- Configure notification channels

## Status

- [x] Core framework (agents, messaging, pipeline)
- [x] Management Hub (compliance, monitoring, task routing)
- [x] Trading Dev — scaffold with paper trading
- [x] Product Dev — skeleton ready for implementation
- [x] Content Dev — skeleton ready for implementation
- [ ] Exchange integration (ccxt)
- [ ] Real strategy implementations
- [ ] Telegram bot integration
- [ ] Database persistence (SQLAlchemy)
