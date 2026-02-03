"""
============================================================
New Task Manager Agent
新任務管理者 - ARD 區域的核心協調者
============================================================

角色定位:
- ARD 區域的「坐鎮」角色
- 所有新任務的入口
- 識別開發/營運模式
- 協調 MasterArchitect 和 SystemPilot

決策邏輯:
- 開發模式 → 指派 MasterArchitect 進行架構解構
- 營運模式 → 指派 SystemPilot 進行執行
- 跨部門任務 → 動態創建項目團隊
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

import sys
sys.path.append('../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class TaskMode(Enum):
    """任務模式"""
    DEVELOPMENT = "development"  # 開發模式
    OPERATION = "operation"      # 營運模式
    HYBRID = "hybrid"           # 混合模式


class TaskPriority(Enum):
    """任務優先級"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKLOG = 5


@dataclass
class TaskDefinition:
    """任務定義"""
    id: str
    title: str
    description: str
    mode: TaskMode
    priority: TaskPriority
    department: str
    assigned_to: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"


class NewTaskManager(BaseAgent):
    """
    新任務管理者 Agent

    📋 ARD 區域核心，負責所有新任務的接收、分析和分派
    """

    SYSTEM_PROMPT = """# 角色定義
你是 AI 組織的新任務管理者 (NewTaskManager)，Zone ARD 的核心協調者。

## 核心職責

### 1. 任務接收與分析
- 接收來自 Secretary 的任務請求
- 分析任務性質（開發/營運）
- 評估任務複雜度和資源需求
- 確定優先級

### 2. 模式識別與路由

#### 開發模式 (Development Mode)
觸發條件:
- 需要建立新的 Agent
- 需要開發新功能
- 需要架構重構
- 需要技術設計

路由目標: **MasterArchitect**

#### 營運模式 (Operation Mode)
觸發條件:
- 日常任務執行
- 系統監控檢查
- 數據更新處理
- 定期報告生成

路由目標: **SystemPilot**

### 3. 項目團隊管理
- 決定是否需要創建動態項目團隊
- 定義團隊規模和組成
- 監督項目進度
- 管理團隊生命週期

### 4. 跨部門協調
- 審批跨部門協作請求
- 協調資源衝突
- 追蹤跨部門任務狀態
- 確保部門間通訊順暢

## 任務分析框架

### 步驟 1: 識別任務類型
問自己:
- 這是創建新東西還是執行現有流程？
- 需要架構設計還是按規則執行？
- 是一次性任務還是週期性任務？

### 步驟 2: 評估複雜度
維度:
- 技術複雜度 (1-5)
- 跨部門依賴 (低/中/高)
- 時間緊迫性 (緊急/正常/低)
- 資源需求 (少/中/多)

### 步驟 3: 分派決策
```
IF 技術複雜度 >= 4 OR 需要新 Agent:
    → MasterArchitect (開發模式)
ELIF 是日常營運任務:
    → SystemPilot (營運模式)
ELIF 需要專門團隊:
    → 創建項目團隊
ELSE:
    → 直接分派給相關部門
```

## 項目團隊配置

### 標準團隊 (Standard)
- 1 Researcher
- 1 Foreman
- 2 Workers

### 擴展團隊 (Extended)
- 1 Researcher
- 1 Foreman
- 3-5 Workers

### 精簡團隊 (Lite)
- 1 Foreman (兼任研究)
- 1-2 Workers

## 輸出格式

### 任務分析報告
```
📋 任務分析報告

【任務 ID】{task_id}
【任務標題】{title}

📊 分析結果
- 任務模式: {DEVELOPMENT/OPERATION/HYBRID}
- 複雜度評分: {1-5}/5
- 跨部門依賴: {低/中/高}
- 優先級: {CRITICAL/HIGH/MEDIUM/LOW}

🎯 分派決策
- 主要負責: {Agent/Team}
- 協作部門: {部門列表}
- 預計工作量: {描述}

📅 執行計劃
1. {階段1}
2. {階段2}
...

⚡ 即時動作
{需要立即執行的動作}
```

### 團隊創建通知
```
🛠 項目團隊創建通知

【項目】{project_name}
【部門】{department}
【團隊配置】
- Researcher: {name}
- Foreman: {name}
- Workers: {count} 人

【任務描述】
{description}

【預期交付】
{deliverables}
```

## 工作原則

1. **快速響應**: 任務分析必須在收到後 2 分鐘內完成
2. **準確分派**: 選擇最適合的執行者
3. **資源優化**: 避免過度分配資源
4. **進度透明**: 實時更新任務狀態
5. **風險前置**: 提前識別潛在阻礙

## 與其他 Agent 的協作

- **Secretary**: 接收任務請求，報告任務狀態
- **SystemPilot**: 委派營運任務，獲取系統容量信息
- **MasterArchitect**: 委派開發任務，獲取架構建議
- **DatabaseChecker**: 獲取數據相關任務的可行性分析
- **ComplianceChecker**: 確保任務符合合規要求

## 特殊指令

- `queue`: 顯示當前任務隊列
- `capacity`: 顯示系統容量和負載
- `escalate {task_id}`: 升級任務優先級
- `reassign {task_id} {agent}`: 重新分派任務
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.PERMANENT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.task_queue: List[TaskDefinition] = []
        self.active_tasks: Dict[str, TaskDefinition] = {}
        self.completed_tasks: List[TaskDefinition] = []
        self.project_teams: Dict[str, Dict] = {}

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理新任務

        Args:
            input_data: {
                "action": str,          # analyze, create_team, update_status, query
                "task": dict,           # 任務詳情
                "team_config": dict     # 團隊配置 (for create_team)
            }

        Returns:
            處理結果
        """
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "analyze")

        if action == "analyze":
            result = self._analyze_task(input_data.get("task", {}))
        elif action == "create_team":
            result = await self._create_project_team(input_data.get("team_config", {}))
        elif action == "update_status":
            result = self._update_task_status(
                input_data.get("task_id"),
                input_data.get("status")
            )
        elif action == "query":
            result = self._query_tasks(input_data.get("filters", {}))
        elif action == "approve_cross_dept":
            result = self._approve_cross_department(input_data.get("request", {}))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _analyze_task(self, task_data: Dict) -> Dict[str, Any]:
        """分析任務並決定分派"""
        title = task_data.get("title", "")
        description = task_data.get("description", "")
        combined = f"{title} {description}".lower()

        # 識別任務模式
        dev_indicators = ['建立', '創建', '開發', '設計', '架構', '重構', 'create', 'build', 'develop']
        ops_indicators = ['執行', '運行', '檢查', '更新', '監控', 'run', 'execute', 'monitor', 'update']

        is_dev = any(ind in combined for ind in dev_indicators)
        is_ops = any(ind in combined for ind in ops_indicators)

        if is_dev and is_ops:
            mode = TaskMode.HYBRID
        elif is_dev:
            mode = TaskMode.DEVELOPMENT
        else:
            mode = TaskMode.OPERATION

        # 評估複雜度
        complexity = 3  # 默認中等
        if 'agent' in combined or 'system' in combined:
            complexity = 4
        if 'simple' in combined or '簡單' in combined:
            complexity = 2

        # 創建任務定義
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task_def = TaskDefinition(
            id=task_id,
            title=title,
            description=description,
            mode=mode,
            priority=TaskPriority(task_data.get("priority", 3)),
            department=task_data.get("department", "general")
        )

        # 決定分派
        if mode == TaskMode.DEVELOPMENT:
            assigned_to = ["MasterArchitect"]
            needs_team = complexity >= 4
        elif mode == TaskMode.OPERATION:
            assigned_to = ["SystemPilot"]
            needs_team = False
        else:
            assigned_to = ["MasterArchitect", "SystemPilot"]
            needs_team = True

        task_def.assigned_to = assigned_to
        self.task_queue.append(task_def)

        return {
            "task_id": task_id,
            "analysis": {
                "mode": mode.value,
                "complexity": complexity,
                "assigned_to": assigned_to,
                "needs_team": needs_team,
                "priority": task_def.priority.name
            },
            "routing": {
                "primary": assigned_to[0],
                "secondary": assigned_to[1] if len(assigned_to) > 1 else None
            },
            "status": "queued"
        }

    async def _create_project_team(self, config: Dict) -> Dict[str, Any]:
        """創建項目團隊"""
        project_id = f"proj_{uuid.uuid4().hex[:8]}"

        team = {
            "project_id": project_id,
            "project_name": config.get("name", "Unnamed Project"),
            "department": config.get("department", "general"),
            "size": config.get("size", "standard"),
            "researcher": f"researcher_{project_id}",
            "foreman": f"foreman_{project_id}",
            "workers": [f"worker_{project_id}_{i}" for i in range(config.get("worker_count", 2))],
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }

        self.project_teams[project_id] = team

        return {
            "status": "created",
            "team": team,
            "message": f"Project team created for {team['project_name']}"
        }

    def _update_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        """更新任務狀態"""
        for task in self.task_queue:
            if task.id == task_id:
                task.status = status
                if status == "completed":
                    self.task_queue.remove(task)
                    self.completed_tasks.append(task)
                return {
                    "status": "updated",
                    "task_id": task_id,
                    "new_status": status
                }

        return {"status": "error", "message": f"Task not found: {task_id}"}

    def _query_tasks(self, filters: Dict) -> Dict[str, Any]:
        """查詢任務"""
        tasks = self.task_queue

        if filters.get("mode"):
            tasks = [t for t in tasks if t.mode.value == filters["mode"]]
        if filters.get("department"):
            tasks = [t for t in tasks if t.department == filters["department"]]
        if filters.get("priority"):
            tasks = [t for t in tasks if t.priority.value <= filters["priority"]]

        return {
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "mode": t.mode.value,
                    "priority": t.priority.name,
                    "status": t.status,
                    "assigned_to": t.assigned_to
                }
                for t in tasks
            ],
            "total": len(tasks),
            "pending_teams": len(self.project_teams)
        }

    def _approve_cross_department(self, request: Dict) -> Dict[str, Any]:
        """審批跨部門協作請求"""
        from_dept = request.get("from_department")
        to_dept = request.get("to_department")
        reason = request.get("reason", "")

        # 簡單的審批邏輯
        approved = True
        if from_dept == to_dept:
            approved = False
            message = "Same department, no cross-department approval needed"
        else:
            message = f"Cross-department collaboration approved: {from_dept} → {to_dept}"

        return {
            "approved": approved,
            "from": from_dept,
            "to": to_dept,
            "message": message,
            "approved_at": datetime.now().isoformat()
        }
