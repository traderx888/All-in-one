"""
============================================================
Project Team Factory
項目團隊工廠 - 動態創建項目團隊
============================================================

根據項目需求動態實例化 Researcher, Foreman, Workers 團隊
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid

from .team_templates import Researcher, Foreman, Worker

import sys
sys.path.append('../../..')
from core.base_agent import AgentType


@dataclass
class ProjectConfig:
    """項目配置"""
    name: str
    description: str
    type: str  # article_rss, polymarket, telegram_bot, etc.
    modules: List[str] = field(default_factory=list)
    worker_count: int = 2
    priority: str = "medium"


@dataclass
class ProjectTeam:
    """項目團隊"""
    project_id: str
    config: ProjectConfig
    researcher: Researcher
    foreman: Foreman
    workers: List[Worker]
    created_at: datetime
    status: str = "active"


class ProjectTeamFactory:
    """
    項目團隊工廠

    負責根據項目需求動態創建和管理項目團隊
    """

    # 預定義的項目模板
    PROJECT_TEMPLATES = {
        "article_rss": {
            "description": "RSS 文章聚合和管理系統",
            "modules": ["rss_parser", "content_filter", "storage", "api"],
            "worker_count": 3
        },
        "polymarket": {
            "description": "Polymarket 預測市場數據分析",
            "modules": ["data_fetcher", "analyzer", "predictor", "reporter"],
            "worker_count": 4
        },
        "telegram_bot": {
            "description": "Telegram 機器人開發",
            "modules": ["bot_core", "handlers", "commands", "integration"],
            "worker_count": 2
        }
    }

    def __init__(self):
        self.active_teams: Dict[str, ProjectTeam] = {}
        self.archived_teams: List[ProjectTeam] = []

    def create_team(self, config: ProjectConfig) -> ProjectTeam:
        """
        創建項目團隊

        Args:
            config: 項目配置

        Returns:
            創建的項目團隊
        """
        project_id = f"proj_{uuid.uuid4().hex[:8]}"

        # 創建 Researcher
        researcher = Researcher(
            agent_id=f"{project_id}_researcher",
            name=f"{config.name}_Researcher"
        )
        researcher.set_project_context({
            "name": config.name,
            "type": config.type,
            "description": config.description
        })

        # 創建 Foreman
        foreman = Foreman(
            agent_id=f"{project_id}_foreman",
            name=f"{config.name}_Foreman"
        )
        foreman.set_project({
            "name": config.name,
            "description": config.description,
            "type": config.type
        })

        # 創建 Workers
        workers = []
        for i, module in enumerate(config.modules[:config.worker_count]):
            worker = Worker(
                agent_id=f"{project_id}_worker_{i}",
                name=f"{config.name}_Worker_{i}",
                specialization=module
            )
            workers.append(worker)

        # 補充額外的通用 Workers
        for i in range(len(workers), config.worker_count):
            worker = Worker(
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
        team = ProjectTeam(
            project_id=project_id,
            config=config,
            researcher=researcher,
            foreman=foreman,
            workers=workers,
            created_at=datetime.now()
        )

        self.active_teams[project_id] = team

        return team

    def create_from_template(self, template_name: str, project_name: str) -> ProjectTeam:
        """
        從模板創建項目團隊

        Args:
            template_name: 模板名稱 (article_rss, polymarket, telegram_bot)
            project_name: 項目名稱

        Returns:
            創建的項目團隊
        """
        if template_name not in self.PROJECT_TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}")

        template = self.PROJECT_TEMPLATES[template_name]

        config = ProjectConfig(
            name=project_name,
            description=template["description"],
            type=template_name,
            modules=template["modules"],
            worker_count=template["worker_count"]
        )

        return self.create_team(config)

    def get_team(self, project_id: str) -> Optional[ProjectTeam]:
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
            "status": team.status,
            "team_members": {
                "researcher": {
                    "id": team.researcher.agent_id,
                    "status": team.researcher.status.value
                },
                "foreman": {
                    "id": team.foreman.agent_id,
                    "status": team.foreman.status.value
                },
                "workers": [
                    {
                        "id": w.agent_id,
                        "specialization": w.specialization,
                        "status": w.status.value
                    }
                    for w in team.workers
                ]
            }
        }


# 預設項目類型說明
PROJECT_TYPES_INFO = """
# 產品開發部支援的項目類型

## 1. Article_RSS
- 描述: RSS 文章聚合和管理系統
- 功能模組:
  - rss_parser: RSS 解析
  - content_filter: 內容過濾
  - storage: 存儲管理
  - api: API 接口
- 建議團隊規模: 3 Workers

## 2. PolyMarket
- 描述: Polymarket 預測市場數據分析
- 功能模組:
  - data_fetcher: 數據獲取
  - analyzer: 數據分析
  - predictor: 預測模型
  - reporter: 報告生成
- 建議團隊規模: 4 Workers

## 3. Telegram Bot
- 描述: Telegram 機器人開發
- 功能模組:
  - bot_core: 機器人核心
  - handlers: 消息處理
  - commands: 指令系統
  - integration: 外部集成
- 建議團隊規模: 2 Workers
"""
