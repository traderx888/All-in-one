"""
============================================================
Orchestrator
組織編排器 - 負責 Agent 生命週期管理
============================================================
"""

from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import yaml

from .base_agent import BaseAgent, AgentType, AgentStatus, AgentContext
from .message_bus import MessageBus

logger = logging.getLogger(__name__)


@dataclass
class ProjectTeam:
    """項目團隊"""
    project_id: str
    project_name: str
    department: str
    researcher: Optional[BaseAgent] = None
    foreman: Optional[BaseAgent] = None
    workers: List[BaseAgent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "active"


class Orchestrator:
    """
    組織編排器

    負責:
    - 常駐 Agent 的初始化和管理
    - 動態項目團隊的創建和銷毀
    - Agent 生命週期管理
    - 資源配額控制
    """

    def __init__(self, config_path: str = "config/organization.yaml"):
        self.config = self._load_config(config_path)
        self.message_bus = MessageBus()

        # Agent 註冊表
        self._permanent_agents: Dict[str, BaseAgent] = {}
        self._project_teams: Dict[str, ProjectTeam] = {}

        # Agent 工廠
        self._agent_factories: Dict[str, Type[BaseAgent]] = {}

    def _load_config(self, path: str) -> Dict:
        """載入配置"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {path}, using defaults")
            return {}

    def register_agent_factory(self, role: str, factory: Type[BaseAgent]):
        """註冊 Agent 工廠"""
        self._agent_factories[role] = factory
        logger.info(f"Registered agent factory for role: {role}")

    async def initialize_permanent_agents(self):
        """初始化所有常駐 Agent"""
        hierarchy = self.config.get("organization", {}).get("hierarchy", [])

        for level in hierarchy:
            agents = level.get("agents", [])
            for agent_name in agents:
                await self._spawn_permanent_agent(agent_name)

            # 處理 zones (Management Hub)
            for zone in level.get("zones", []):
                for agent_name in zone.get("agents", []):
                    await self._spawn_permanent_agent(agent_name, zone=zone.get("name"))

        logger.info(f"Initialized {len(self._permanent_agents)} permanent agents")

    async def _spawn_permanent_agent(self, name: str, zone: Optional[str] = None):
        """生成常駐 Agent"""
        if name in self._agent_factories:
            agent = self._agent_factories[name](
                agent_id=f"perm_{name.lower()}_{datetime.now().strftime('%Y%m%d')}",
                name=name,
                role=name,
                agent_type=AgentType.PERMANENT
            )
            self._permanent_agents[name] = agent

            # 訂閱消息總線
            self.message_bus.subscribe(
                agent.agent_id,
                agent.receive_message
            )

            logger.info(f"Spawned permanent agent: {name}")
        else:
            logger.warning(f"No factory registered for agent: {name}")

    async def spawn_project_team(
        self,
        project_id: str,
        project_name: str,
        department: str,
        worker_count: int = 2
    ) -> ProjectTeam:
        """
        動態生成項目團隊

        Args:
            project_id: 項目 ID
            project_name: 項目名稱
            department: 所屬部門
            worker_count: Worker 數量

        Returns:
            創建的項目團隊
        """
        # 檢查資源配額
        quotas = self.config.get("resource_quotas", {})
        if len(self._project_teams) >= quotas.get("max_concurrent_projects", 10):
            raise ResourceError("已達到最大並發項目數限制")

        if worker_count > quotas.get("max_workers_per_project", 5):
            worker_count = quotas.get("max_workers_per_project", 5)
            logger.warning(f"Worker count capped at {worker_count}")

        team = ProjectTeam(
            project_id=project_id,
            project_name=project_name,
            department=department
        )

        # 創建團隊成員
        context = AgentContext(
            task_id=project_id,
            department=department,
            project=project_name
        )

        # Researcher
        if "Researcher" in self._agent_factories:
            team.researcher = self._agent_factories["Researcher"](
                agent_id=f"proj_{project_id}_researcher",
                name=f"{project_name}_Researcher",
                role="Researcher",
                agent_type=AgentType.PROJECT
            )
            team.researcher.set_context(context)

        # Foreman
        if "Foreman" in self._agent_factories:
            team.foreman = self._agent_factories["Foreman"](
                agent_id=f"proj_{project_id}_foreman",
                name=f"{project_name}_Foreman",
                role="Foreman",
                agent_type=AgentType.PROJECT
            )
            team.foreman.set_context(context)

        # Workers
        if "Worker" in self._agent_factories:
            for i in range(worker_count):
                worker = self._agent_factories["Worker"](
                    agent_id=f"proj_{project_id}_worker_{i}",
                    name=f"{project_name}_Worker_{i}",
                    role="Worker",
                    agent_type=AgentType.PROJECT
                )
                worker.set_context(context)
                team.workers.append(worker)

        self._project_teams[project_id] = team
        logger.info(f"Spawned project team for: {project_name} with {worker_count} workers")

        return team

    async def terminate_project_team(self, project_id: str):
        """終止項目團隊"""
        if project_id not in self._project_teams:
            logger.warning(f"Project team not found: {project_id}")
            return

        team = self._project_teams[project_id]

        # 更新所有成員狀態
        if team.researcher:
            team.researcher.update_status(AgentStatus.TERMINATED)
        if team.foreman:
            team.foreman.update_status(AgentStatus.TERMINATED)
        for worker in team.workers:
            worker.update_status(AgentStatus.TERMINATED)

        team.status = "terminated"
        del self._project_teams[project_id]

        logger.info(f"Terminated project team: {project_id}")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """獲取常駐 Agent"""
        return self._permanent_agents.get(name)

    def get_project_team(self, project_id: str) -> Optional[ProjectTeam]:
        """獲取項目團隊"""
        return self._project_teams.get(project_id)

    def get_all_agents(self) -> Dict[str, Any]:
        """獲取所有 Agent 狀態"""
        result = {
            "permanent": {
                name: agent.get_status_report()
                for name, agent in self._permanent_agents.items()
            },
            "project_teams": {
                pid: {
                    "name": team.project_name,
                    "department": team.department,
                    "status": team.status,
                    "researcher": team.researcher.get_status_report() if team.researcher else None,
                    "foreman": team.foreman.get_status_report() if team.foreman else None,
                    "workers": [w.get_status_report() for w in team.workers]
                }
                for pid, team in self._project_teams.items()
            }
        }
        return result

    def get_stats(self) -> Dict[str, Any]:
        """獲取組織統計"""
        total_workers = sum(
            len(team.workers) for team in self._project_teams.values()
        )
        return {
            "permanent_agents": len(self._permanent_agents),
            "active_projects": len(self._project_teams),
            "total_project_workers": total_workers,
            "message_bus": self.message_bus.get_stats()
        }


class ResourceError(Exception):
    """資源錯誤"""
    pass
