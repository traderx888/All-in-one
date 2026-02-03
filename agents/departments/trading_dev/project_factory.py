"""
============================================================
Trading Project Team Factory
交易項目團隊工廠 - 動態創建交易開發團隊
============================================================
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid

from .team_templates import TradingResearcher, TradingForeman, TradingWorker

import sys
sys.path.append('../../..')
from core.base_agent import AgentType


@dataclass
class TradingProjectConfig:
    """交易項目配置"""
    name: str
    description: str
    type: str  # daytrade_engine, auto_trading_system, signal_alert
    market: str = "crypto"
    modules: List[str] = field(default_factory=list)
    worker_count: int = 2
    risk_level: str = "medium"


@dataclass
class TradingProjectTeam:
    """交易項目團隊"""
    project_id: str
    config: TradingProjectConfig
    researcher: TradingResearcher
    foreman: TradingForeman
    workers: List[TradingWorker]
    created_at: datetime
    status: str = "active"


class TradingProjectFactory:
    """
    交易項目團隊工廠

    負責根據項目需求動態創建和管理交易開發團隊
    """

    # 預定義的項目模板
    PROJECT_TEMPLATES = {
        "daytrade_engine": {
            "description": "日內交易引擎 - 支持快速下單和日內風控",
            "modules": ["market_data", "order_engine", "risk_manager", "pnl_calculator"],
            "worker_count": 3,
            "risk_level": "high"
        },
        "auto_trading_system": {
            "description": "自動交易系統 - 策略執行和倉位管理",
            "modules": ["strategy_engine", "signal_processor", "position_manager", "risk_controller", "reporter"],
            "worker_count": 4,
            "risk_level": "high"
        },
        "signal_alert": {
            "description": "交易信號提醒 - 信號生成和多渠道推送",
            "modules": ["signal_generator", "alert_dispatcher", "history_tracker"],
            "worker_count": 2,
            "risk_level": "medium"
        }
    }

    def __init__(self):
        self.active_teams: Dict[str, TradingProjectTeam] = {}
        self.archived_teams: List[TradingProjectTeam] = []

    def create_team(self, config: TradingProjectConfig) -> TradingProjectTeam:
        """
        創建交易項目團隊

        Args:
            config: 項目配置

        Returns:
            創建的項目團隊
        """
        project_id = f"trading_proj_{uuid.uuid4().hex[:8]}"

        # 創建 TradingResearcher
        researcher = TradingResearcher(
            agent_id=f"{project_id}_researcher",
            name=f"{config.name}_Researcher"
        )
        researcher.set_project_context({
            "name": config.name,
            "type": config.type,
            "market": config.market
        })

        # 創建 TradingForeman
        foreman = TradingForeman(
            agent_id=f"{project_id}_foreman",
            name=f"{config.name}_Foreman"
        )
        foreman.set_project({
            "name": config.name,
            "type": config.type,
            "market": config.market,
            "risk_level": config.risk_level
        })

        # 創建 TradingWorkers
        workers = []
        for i, module in enumerate(config.modules[:config.worker_count]):
            worker = TradingWorker(
                agent_id=f"{project_id}_worker_{i}",
                name=f"{config.name}_Worker_{i}",
                specialization=module
            )
            workers.append(worker)

        # 補充額外的通用 Workers
        for i in range(len(workers), config.worker_count):
            worker = TradingWorker(
                agent_id=f"{project_id}_worker_{i}",
                name=f"{config.name}_Worker_{i}"
            )
            workers.append(worker)

        # 設置團隊關係
        team_dict = {
            "researcher": researcher,
            "foreman": foreman,
            "workers": workers
        }
        foreman.set_team(team_dict)

        # 創建團隊對象
        team = TradingProjectTeam(
            project_id=project_id,
            config=config,
            researcher=researcher,
            foreman=foreman,
            workers=workers,
            created_at=datetime.now()
        )

        self.active_teams[project_id] = team

        return team

    def create_from_template(self, template_name: str, project_name: str, market: str = "crypto") -> TradingProjectTeam:
        """
        從模板創建項目團隊

        Args:
            template_name: 模板名稱 (daytrade_engine, auto_trading_system, signal_alert)
            project_name: 項目名稱
            market: 目標市場

        Returns:
            創建的項目團隊
        """
        if template_name not in self.PROJECT_TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}")

        template = self.PROJECT_TEMPLATES[template_name]

        config = TradingProjectConfig(
            name=project_name,
            description=template["description"],
            type=template_name,
            market=market,
            modules=template["modules"],
            worker_count=template["worker_count"],
            risk_level=template["risk_level"]
        )

        return self.create_team(config)

    def get_team(self, project_id: str) -> Optional[TradingProjectTeam]:
        """獲取團隊"""
        return self.active_teams.get(project_id)

    def archive_team(self, project_id: str) -> bool:
        """歸檔團隊"""
        if project_id in self.active_teams:
            team = self.active_teams.pop(project_id)
            team.status = "archived"
            self.archived_teams.append(team)
            return True
        return False

    def list_active_teams(self) -> List[Dict[str, Any]]:
        """列出活躍團隊"""
        return [
            {
                "project_id": team.project_id,
                "name": team.config.name,
                "type": team.config.type,
                "market": team.config.market,
                "risk_level": team.config.risk_level,
                "worker_count": len(team.workers),
                "created_at": team.created_at.isoformat(),
                "status": team.status
            }
            for team in self.active_teams.values()
        ]

    def get_team_status(self, project_id: str) -> Dict[str, Any]:
        """獲取團隊狀態"""
        team = self.active_teams.get(project_id)
        if not team:
            return {"error": f"Team not found: {project_id}"}

        return {
            "project_id": project_id,
            "name": team.config.name,
            "type": team.config.type,
            "risk_level": team.config.risk_level,
            "status": team.status,
            "team_members": {
                "researcher": {
                    "id": team.researcher.agent_id,
                    "status": team.researcher.status.value
                },
                "foreman": {
                    "id": team.foreman.agent_id,
                    "status": team.foreman.status.value,
                    "risk_checks": team.foreman.risk_checks
                },
                "workers": [
                    {
                        "id": w.agent_id,
                        "specialization": w.specialization,
                        "status": w.status.value
                    }
                    for w in team.workers
                ]
            },
            "risk_disclaimer": "⚠️ 交易涉及重大風險，可能損失全部本金。過往表現不代表未來收益。"
        }


# 預設項目類型說明
TRADING_PROJECT_TYPES_INFO = """
# 交易開發部支援的項目類型

## 1. Daytrade Engine (日內交易引擎)
- 描述: 支持快速下單和日內風控的交易引擎
- 功能模組:
  - market_data: 實時行情處理
  - order_engine: 下單執行引擎
  - risk_manager: 風險管理
  - pnl_calculator: 盈虧計算
- 風險等級: 高
- 建議團隊規模: 3 Workers

## 2. Auto Trading System (自動交易系統)
- 描述: 自動化策略執行和倉位管理系統
- 功能模組:
  - strategy_engine: 策略執行引擎
  - signal_processor: 信號處理
  - position_manager: 倉位管理
  - risk_controller: 風控系統
  - reporter: 報告生成
- 風險等級: 高
- 建議團隊規模: 4 Workers

## 3. Signal Alert (信號提醒)
- 描述: 交易信號生成和多渠道推送系統
- 功能模組:
  - signal_generator: 信號生成
  - alert_dispatcher: 提醒分發
  - history_tracker: 歷史追蹤
- 風險等級: 中
- 建議團隊規模: 2 Workers

---

⚠️ **重要風險提示**

交易涉及重大風險，包括但不限於：
- 可能損失全部投入資金
- 槓桿交易會放大風險
- 市場波動可能導致快速損失
- 技術故障可能影響交易執行
- 歷史回測結果不代表未來表現

使用本部門開發的任何交易系統前，請確保：
1. 充分了解相關風險
2. 只用能承受損失的資金
3. 進行充分的模擬測試
4. 設置適當的風控參數
"""
