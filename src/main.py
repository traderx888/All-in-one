"""
All-in-One Multi-Agent Trading System
======================================

Main entry point. Boots the entire agent hierarchy:

    User (CEO)
    ├── Secretary (Secy)
    ├── Library (Librarian)
    └── Management Hub
        ├── Zone LAW: ComplianceChecker
        └── Zone ARD: SystemPilot, TaskManager, DatabaseChecker, MasterArchitect
            ├── Trading Dev
            │   ├── Daytrade Engine   (Researcher → Foreman → Workers)
            │   ├── Auto Trading      (Researcher → Foreman → Workers)
            │   └── Signal Alert      (Researcher → Foreman → Workers)
            ├── Product Dev
            │   ├── Article_RSS       (Researcher → Foreman → Workers)
            │   ├── PolyMarket        (Researcher → Foreman → Workers)
            │   └── Telegram Bot      (Researcher → Foreman → Workers)
            └── Content Dev
                ├── Content Pilot → TrafficMonitor → DataAnalyst
                ├── Booster Chain: KPI → Campaign
                └── Content Chain: PA → CMD → Generator → ArticleKeeper

Usage:
    python -m src.main              # Run with default config
    python -m src.main --config config/settings.yaml
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import structlog
import yaml

from src.core.message import MessageBus
from src.core.agent_registry import AgentRegistry

# CEO layer
from src.ceo.secretary import Secretary
from src.ceo.librarian import Librarian

# Management Hub
from src.management_hub.compliance_checker import ComplianceChecker
from src.management_hub.system_pilot import SystemPilot
from src.management_hub.task_manager import TaskManager
from src.management_hub.database_checker import DatabaseChecker
from src.management_hub.master_architect import MasterArchitect

# Trading Dev
from src.trading_dev.division import TradingDevDivision
from src.trading_dev.daytrade_engine import DaytradeResearcher, DaytradeForeman, DaytradeWorker
from src.trading_dev.auto_trading import AutoTradingResearcher, AutoTradingForeman, AutoTradingWorker
from src.trading_dev.signal_alert import SignalResearcher, SignalForeman, SignalWorker

# Product Dev
from src.product_dev.division import ProductDevDivision
from src.product_dev.article_rss import ArticleRSSResearcher, ArticleRSSForeman, ArticleRSSWorker
from src.product_dev.polymarket import PolymarketResearcher, PolymarketForeman, PolymarketWorker
from src.product_dev.telegram_bot import TelegramBotResearcher, TelegramBotForeman, TelegramBotWorker

# Content Dev
from src.content_dev.division import ContentDevDivision
from src.content_dev.content_pilot import ContentPilot
from src.content_dev.traffic_monitor import TrafficMonitor
from src.content_dev.data_analyst import DataAnalyst
from src.content_dev.booster_chain import KPIAgent, CampaignAgent
from src.content_dev.content_chain import PAAgent, CMDAgent, GeneratorAgent, ArticleKeeperAgent


def load_config(config_path: str = "config/settings.yaml") -> dict:
    path = Path(config_path)
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f)
    return {}


def setup_logging(level: str = "INFO") -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog, level.upper(), structlog.INFO) if hasattr(structlog, level.upper()) else 20
        ),
    )


def build_system(config: dict) -> tuple[MessageBus, AgentRegistry, list]:
    """Construct the entire agent hierarchy."""
    bus = MessageBus()
    registry = AgentRegistry()
    agents = []

    trading_cfg = config.get("trading", {})
    divisions_cfg = config.get("divisions", {})

    # ──────────────────────────────────────────────
    # CEO Layer
    # ──────────────────────────────────────────────
    secretary = Secretary(bus)
    librarian = Librarian(bus)
    agents.extend([secretary, librarian])

    # ──────────────────────────────────────────────
    # Management Hub
    # ──────────────────────────────────────────────
    compliance = ComplianceChecker(bus, config={
        "max_open_positions": trading_cfg.get("max_open_positions", 5),
        "max_drawdown_pct": trading_cfg.get("max_drawdown_pct", 10.0),
        "risk_per_trade_pct": trading_cfg.get("risk_per_trade_pct", 1.0),
    })
    system_pilot = SystemPilot(bus, registry)
    task_manager = TaskManager(bus)
    db_checker = DatabaseChecker(bus)
    architect = MasterArchitect(bus, registry, config=config)
    agents.extend([compliance, system_pilot, task_manager, db_checker, architect])

    # ──────────────────────────────────────────────
    # Trading Dev Division
    # ──────────────────────────────────────────────
    trading_dev_cfg = divisions_cfg.get("trading_dev", {})
    if trading_dev_cfg.get("enabled", True):
        trading_div = TradingDevDivision(bus, registry)
        agents.append(trading_div)

        # -- Daytrade Engine --
        dt_cfg = trading_dev_cfg.get("daytrade_engine", {})
        if dt_cfg.get("enabled", True):
            dt_researcher = DaytradeResearcher(bus, config={
                "watchlist": trading_cfg.get("watchlist", []),
                "timeframe": trading_cfg.get("default_timeframe", "5m"),
                "strategies": dt_cfg.get("strategies", ["momentum"]),
            })
            dt_foreman = DaytradeForeman(bus, config={
                "worker_names": ["daytrade_worker_1", "daytrade_worker_2"],
            })
            dt_worker_1 = DaytradeWorker("daytrade_worker_1", bus, config={
                "mode": trading_dev_cfg.get("auto_trading", {}).get("mode", "paper"),
            })
            dt_worker_2 = DaytradeWorker("daytrade_worker_2", bus, config={
                "mode": trading_dev_cfg.get("auto_trading", {}).get("mode", "paper"),
            })
            agents.extend([dt_researcher, dt_foreman, dt_worker_1, dt_worker_2])

        # -- Auto Trading System --
        at_cfg = trading_dev_cfg.get("auto_trading", {})
        if at_cfg.get("enabled", True):
            at_researcher = AutoTradingResearcher(bus)
            at_foreman = AutoTradingForeman(bus, config={
                "worker_names": ["auto_trading_worker_1"],
            })
            at_worker = AutoTradingWorker("auto_trading_worker_1", bus, config={
                "mode": at_cfg.get("mode", "paper"),
            })
            agents.extend([at_researcher, at_foreman, at_worker])

        # -- Signal Alert --
        sa_cfg = trading_dev_cfg.get("signal_alert", {})
        if sa_cfg.get("enabled", True):
            sa_researcher = SignalResearcher(bus, config={
                "watchlist": trading_cfg.get("watchlist", []),
            })
            sa_foreman = SignalForeman(bus, config={
                "worker_names": ["signal_worker_1"],
                "channels": sa_cfg.get("channels", ["console"]),
            })
            sa_worker = SignalWorker("signal_worker_1", bus)
            agents.extend([sa_researcher, sa_foreman, sa_worker])

    # ──────────────────────────────────────────────
    # Product Dev Division
    # ──────────────────────────────────────────────
    product_dev_cfg = divisions_cfg.get("product_dev", {})
    if product_dev_cfg.get("enabled", False):
        product_div = ProductDevDivision(bus, registry)
        agents.append(product_div)

        if product_dev_cfg.get("article_rss", {}).get("enabled", False):
            agents.extend([
                ArticleRSSResearcher(bus),
                ArticleRSSForeman(bus),
                ArticleRSSWorker("article_rss_worker_1", bus),
            ])

        if product_dev_cfg.get("polymarket", {}).get("enabled", False):
            agents.extend([
                PolymarketResearcher(bus),
                PolymarketForeman(bus),
                PolymarketWorker("polymarket_worker_1", bus),
            ])

        if product_dev_cfg.get("telegram_bot", {}).get("enabled", False):
            agents.extend([
                TelegramBotResearcher(bus),
                TelegramBotForeman(bus),
                TelegramBotWorker("telegram_bot_worker_1", bus),
            ])

    # ──────────────────────────────────────────────
    # Content Dev Division
    # ──────────────────────────────────────────────
    if divisions_cfg.get("content_dev", {}).get("enabled", False):
        content_div = ContentDevDivision(bus, registry)
        content_pilot = ContentPilot(bus)
        traffic_mon = TrafficMonitor(bus)
        analyst = DataAnalyst(bus)
        kpi = KPIAgent(bus)
        campaign = CampaignAgent(bus)
        pa = PAAgent(bus)
        cmd = CMDAgent(bus)
        gen = GeneratorAgent(bus)
        keeper = ArticleKeeperAgent(bus)
        agents.extend([
            content_div, content_pilot, traffic_mon, analyst,
            kpi, campaign, pa, cmd, gen, keeper,
        ])

    # Register all agents
    for agent in agents:
        registry.register(agent)

    return bus, registry, agents


async def run(config: dict) -> None:
    """Boot and run the multi-agent system."""
    log = structlog.get_logger()

    bus, registry, agents = build_system(config)

    # Start all agents
    log.info("starting_system", agent_count=len(agents))
    await registry.start_all()

    # Start message bus
    bus_task = asyncio.create_task(bus.start())

    # Print system summary
    summary = registry.summary()
    log.info(
        "system_ready",
        total_agents=summary["total"],
        running=summary["running"],
    )

    # Keep running until interrupted
    try:
        await bus_task
    except asyncio.CancelledError:
        pass
    finally:
        log.info("shutting_down")
        await bus.stop()
        await registry.stop_all()
        log.info("system_stopped")


def main() -> None:
    config_path = "config/settings.yaml"
    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        config_path = sys.argv[2]

    config = load_config(config_path)
    setup_logging(config.get("system", {}).get("log_level", "INFO"))

    log = structlog.get_logger()
    log.info("all_in_one_trading_system", version=config.get("system", {}).get("version", "0.1.0"))

    try:
        asyncio.run(run(config))
    except KeyboardInterrupt:
        log.info("interrupted_by_user")


if __name__ == "__main__":
    main()
