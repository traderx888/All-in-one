#!/usr/bin/env python3
"""
============================================================
All-in-One AI Organization
完整 AI 組織架構 - 主入口
============================================================

這是一個完整的 AI 組織架構系統，包含：
- Executive Level: Secretary (CEO秘書), Librarian (知識庫管理)
- Management Hub: ARD (Agent資源開發) + LAW (合規審計)
- Departments: Content Dev, Product Dev, Trading Dev

使用方式：
1. 通過 Secretary 提交指令
2. Secretary 解析意圖並路由到適當的部門
3. 各部門執行任務並回報結果
"""

import asyncio
from typing import Dict, Any, Optional

# Core
from core.orchestrator import Orchestrator
from core.message_bus import MessageBus

# Executive
from agents.executive import Secretary, Librarian

# Management Hub
from agents.management_hub.ard import (
    SystemPilot,
    NewTaskManager,
    DatabaseChecker,
    MasterArchitect
)
from agents.management_hub.law import ComplianceChecker

# Departments
from agents.departments.content_dev import (
    ContentPilot,
    TrafficMonitor,
    DataAnalyst,
    KPIAgent,
    CampaignAgent,
    PAAgent,
    CMDAgent,
    GeneratorAgent,
    ArticleKeeperAgent
)
from agents.departments.product_dev import ProjectTeamFactory
from agents.departments.trading_dev import TradingProjectFactory


class AIOrganization:
    """
    AI 組織總控制器

    負責初始化和管理整個 AI 組織
    """

    def __init__(self):
        self.orchestrator = Orchestrator()
        self.message_bus = MessageBus()

        # Executive Level
        self.secretary: Optional[Secretary] = None
        self.librarian: Optional[Librarian] = None

        # Management Hub
        self.system_pilot: Optional[SystemPilot] = None
        self.new_task_manager: Optional[NewTaskManager] = None
        self.database_checker: Optional[DatabaseChecker] = None
        self.master_architect: Optional[MasterArchitect] = None
        self.compliance_checker: Optional[ComplianceChecker] = None

        # Content Dev
        self.content_pilot: Optional[ContentPilot] = None
        self.traffic_monitor: Optional[TrafficMonitor] = None
        self.data_analyst: Optional[DataAnalyst] = None

        # Project Factories
        self.product_dev_factory: Optional[ProjectTeamFactory] = None
        self.trading_dev_factory: Optional[TradingProjectFactory] = None

        # 初始化狀態
        self._initialized = False

    async def initialize(self):
        """初始化整個 AI 組織"""
        print("🏢 正在初始化 AI 組織...")

        # 初始化 Executive Level
        print("  📍 初始化 Executive Level...")
        self.secretary = Secretary(
            agent_id="exec_secretary",
            name="Secretary",
            role="CEO Secretary"
        )
        self.librarian = Librarian(
            agent_id="exec_librarian",
            name="Librarian",
            role="Knowledge Manager"
        )

        # 初始化 Management Hub - ARD
        print("  📍 初始化 Management Hub - ARD...")
        self.system_pilot = SystemPilot(
            agent_id="ard_system_pilot",
            name="SystemPilot",
            role="System Operations"
        )
        self.new_task_manager = NewTaskManager(
            agent_id="ard_task_manager",
            name="NewTaskManager",
            role="Task Coordination"
        )
        self.database_checker = DatabaseChecker(
            agent_id="ard_db_checker",
            name="DatabaseChecker",
            role="Database Management"
        )
        self.master_architect = MasterArchitect(
            agent_id="ard_architect",
            name="MasterArchitect",
            role="Architecture Design"
        )

        # 初始化 Management Hub - LAW
        print("  📍 初始化 Management Hub - LAW...")
        self.compliance_checker = ComplianceChecker(
            agent_id="law_compliance",
            name="ComplianceChecker",
            role="Compliance & Audit"
        )

        # 初始化 Content Dev
        print("  📍 初始化 Content Dev...")
        self.content_pilot = ContentPilot(
            agent_id="content_pilot",
            name="ContentPilot",
            role="Content Operations"
        )
        self.traffic_monitor = TrafficMonitor(
            agent_id="content_traffic",
            name="TrafficMonitor",
            role="Traffic Monitoring"
        )
        self.data_analyst = DataAnalyst(
            agent_id="content_analyst",
            name="DataAnalyst",
            role="Data Analysis"
        )

        # 初始化 Project Factories
        print("  📍 初始化 Project Factories...")
        self.product_dev_factory = ProjectTeamFactory()
        self.trading_dev_factory = TradingProjectFactory()

        self._initialized = True
        print("✅ AI 組織初始化完成！")

        return self

    async def process_ceo_request(self, request: str) -> Dict[str, Any]:
        """
        處理 CEO 請求

        這是與 AI 組織互動的主要入口

        Args:
            request: CEO 的指令文本

        Returns:
            處理結果
        """
        if not self._initialized:
            await self.initialize()

        print(f"\n👑 CEO 指令: {request}")
        print("=" * 50)

        # 1. Secretary 解析意圖
        secretary_result = await self.secretary.process({
            "message": request
        })

        print(f"\n📋 Secretary 分析結果:")
        print(secretary_result.get("response", ""))

        # 2. 根據路由決策執行
        routing = secretary_result.get("routing_decision", {})
        primary_route = routing.get("primary_route", "")

        # 這裡可以擴展更複雜的路由邏輯
        if primary_route == "ARD":
            # 路由到 ARD
            if "NewTaskManager" in routing.get("agents", []):
                task_result = await self.new_task_manager.process({
                    "action": "analyze",
                    "task": {
                        "title": request,
                        "description": request
                    }
                })
                return {
                    "secretary_analysis": secretary_result,
                    "task_analysis": task_result
                }

        elif primary_route == "LAW":
            # 路由到 LAW
            compliance_result = await self.compliance_checker.process({
                "action": "check",
                "content_type": "article",
                "content": request
            })
            return {
                "secretary_analysis": secretary_result,
                "compliance_check": compliance_result
            }

        return {
            "secretary_analysis": secretary_result,
            "status": "routed",
            "message": f"Request routed to {primary_route}"
        }

    async def create_product_project(self, template: str, name: str) -> Dict[str, Any]:
        """創建產品開發項目"""
        if not self._initialized:
            await self.initialize()

        team = self.product_dev_factory.create_from_template(template, name)
        return {
            "status": "created",
            "project_id": team.project_id,
            "team": {
                "researcher": team.researcher.agent_id,
                "foreman": team.foreman.agent_id,
                "workers": [w.agent_id for w in team.workers]
            }
        }

    async def create_trading_project(self, template: str, name: str, market: str = "crypto") -> Dict[str, Any]:
        """創建交易開發項目"""
        if not self._initialized:
            await self.initialize()

        team = self.trading_dev_factory.create_from_template(template, name, market)
        return {
            "status": "created",
            "project_id": team.project_id,
            "team": {
                "researcher": team.researcher.agent_id,
                "foreman": team.foreman.agent_id,
                "workers": [w.agent_id for w in team.workers]
            },
            "risk_disclaimer": "⚠️ 交易涉及重大風險"
        }

    def get_organization_status(self) -> Dict[str, Any]:
        """獲取組織狀態"""
        return {
            "initialized": self._initialized,
            "executive": {
                "secretary": self.secretary.status.value if self.secretary else "not_initialized",
                "librarian": self.librarian.status.value if self.librarian else "not_initialized"
            },
            "management_hub": {
                "ard": {
                    "system_pilot": self.system_pilot.status.value if self.system_pilot else "not_initialized",
                    "new_task_manager": self.new_task_manager.status.value if self.new_task_manager else "not_initialized",
                    "database_checker": self.database_checker.status.value if self.database_checker else "not_initialized",
                    "master_architect": self.master_architect.status.value if self.master_architect else "not_initialized"
                },
                "law": {
                    "compliance_checker": self.compliance_checker.status.value if self.compliance_checker else "not_initialized"
                }
            },
            "content_dev": {
                "content_pilot": self.content_pilot.status.value if self.content_pilot else "not_initialized",
                "traffic_monitor": self.traffic_monitor.status.value if self.traffic_monitor else "not_initialized",
                "data_analyst": self.data_analyst.status.value if self.data_analyst else "not_initialized"
            },
            "product_dev": {
                "active_projects": len(self.product_dev_factory.active_teams) if self.product_dev_factory else 0
            },
            "trading_dev": {
                "active_projects": len(self.trading_dev_factory.active_teams) if self.trading_dev_factory else 0
            }
        }


# Demo 函數
async def demo():
    """演示 AI 組織運作"""
    org = AIOrganization()
    await org.initialize()

    print("\n" + "=" * 60)
    print("📊 組織狀態:")
    print("=" * 60)
    import json
    print(json.dumps(org.get_organization_status(), indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("🧪 測試 CEO 指令:")
    print("=" * 60)

    # 測試開發類指令
    result1 = await org.process_ceo_request("建立一個新的交易信號監控 Agent")
    print(f"\n結果: {json.dumps(result1, indent=2, ensure_ascii=False, default=str)}")

    # 測試創建產品項目
    print("\n" + "=" * 60)
    print("🛠️ 創建產品開發項目:")
    print("=" * 60)
    project = await org.create_product_project("telegram_bot", "MyTelegramBot")
    print(f"結果: {json.dumps(project, indent=2, ensure_ascii=False)}")

    # 測試創建交易項目
    print("\n" + "=" * 60)
    print("📈 創建交易開發項目:")
    print("=" * 60)
    trading_project = await org.create_trading_project("signal_alert", "CryptoSignals", "crypto")
    print(f"結果: {json.dumps(trading_project, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    asyncio.run(demo())
