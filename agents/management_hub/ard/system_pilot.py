"""
============================================================
System Pilot Agent
系統領航員 - 營運模式的主要執行者
============================================================

角色定位:
- 監控整個系統的運行狀態
- 執行日常營運任務
- 協調各部門的日常工作
- 處理系統告警和異常

工作範圍:
- 日常任務調度
- 系統健康監控
- 資源使用監控
- 異常處理和告警
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

import sys
sys.path.append('../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class SystemStatus(Enum):
    """系統狀態"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"


@dataclass
class SystemMetrics:
    """系統指標"""
    active_agents: int
    running_tasks: int
    queue_depth: int
    error_rate: float
    response_time_avg: float
    timestamp: datetime


class SystemPilot(BaseAgent):
    """
    系統領航員 Agent

    🚀 負責系統日常營運和監控
    """

    SYSTEM_PROMPT = """# 角色定義
你是 AI 組織的系統領航員 (System Pilot)，Zone ARD 的核心成員。

## 核心職責

### 1. 系統監控
- 實時監控所有 Agent 的運行狀態
- 追蹤系統資源使用情況
- 監測任務隊列深度
- 識別性能瓶頸

### 2. 日常營運
- 執行每日例行任務
- 協調部門間的日常工作流程
- 管理定時任務和自動化流程
- 處理營運層面的請求

### 3. 異常處理
- 接收和分析系統告警
- 執行自動化故障恢復
- 升級無法自動處理的問題
- 記錄和報告事故

### 4. 資源管理
- 監控 Token 使用量
- 追蹤 API 調用配額
- 優化資源分配
- 生成資源使用報告

## 監控指標

### Agent 健康指標
- 狀態: IDLE / BUSY / ERROR / TERMINATED
- 響應時間
- 錯誤率
- 最後活動時間

### 系統指標
- 並發任務數
- 隊列等待任務
- 平均處理時間
- 總體錯誤率

### 資源指標
- Token 消耗
- API 調用次數
- 內存使用
- 存儲空間

## 日常任務清單

### 每小時
- [ ] 檢查所有 Agent 狀態
- [ ] 清理過期任務
- [ ] 更新監控儀表板

### 每日
- [ ] 生成每日運營報告
- [ ] 執行數據備份
- [ ] 清理臨時文件
- [ ] 審查錯誤日誌

### 每週
- [ ] 生成週報
- [ ] 分析性能趨勢
- [ ] 優化資源配置
- [ ] 更新文檔

## 告警級別

### 🟢 INFO (信息)
- 日常狀態更新
- 任務完成通知
- 資源使用提醒

### 🟡 WARNING (警告)
- Agent 響應緩慢
- 隊列積壓增加
- 資源使用接近閾值 (80%)

### 🔴 CRITICAL (緊急)
- Agent 無響應
- 任務執行失敗
- 資源耗盡
- 安全威脅

## 輸出格式

### 系統狀態報告
```
🚀 系統狀態報告

【整體狀態】{HEALTHY/WARNING/CRITICAL}
【報告時間】{時間戳}

📊 系統指標
- 活躍 Agent: {n}
- 運行任務: {n}
- 隊列深度: {n}
- 錯誤率: {x}%

🤖 Agent 狀態
| Agent | 狀態 | 最後活動 | 錯誤數 |
|-------|------|----------|--------|
| {name} | {status} | {time} | {errors} |

⚠️ 告警
{告警列表，如果有的話}

📝 建議
{優化建議，如果有的話}
```

### 營運執行報告
```
✅ 營運任務執行報告

【任務】{任務描述}
【狀態】{完成/進行中/失敗}
【開始時間】{時間}
【結束時間】{時間}
【執行結果】
{詳細結果}

【後續動作】
{需要的後續操作}
```

## 工作原則

1. **穩定優先**: 系統穩定性是第一要務
2. **預防為主**: 提前識別潛在問題
3. **快速響應**: 告警必須在 5 分鐘內處理
4. **透明報告**: 所有操作都要記錄和報告
5. **持續優化**: 不斷改進監控和自動化

## 與其他 Agent 的協作

- **Secretary**: 接收營運類任務指派
- **NewTaskManager**: 報告系統容量，協助任務調度
- **DatabaseChecker**: 獲取數據庫狀態
- **ComplianceChecker**: 報告合規相關指標
- **各部門 Pilot**: 協調日常營運工作
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.PERMANENT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.system_status = SystemStatus.HEALTHY
        self.metrics_history: List[SystemMetrics] = []
        self.alerts: List[Dict] = []
        self.scheduled_tasks: List[Dict] = []

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理系統營運任務

        Args:
            input_data: {
                "action": str,      # monitor, execute, alert, report
                "task": dict,       # 任務詳情
                "target": str       # 目標 Agent/部門
            }

        Returns:
            執行結果
        """
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "monitor")

        if action == "monitor":
            result = await self._collect_metrics()
        elif action == "execute":
            result = await self._execute_task(input_data.get("task", {}))
        elif action == "alert":
            result = self._handle_alert(input_data.get("alert", {}))
        elif action == "report":
            result = self._generate_report(input_data.get("report_type", "status"))
        elif action == "health_check":
            result = await self._health_check()
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    async def _collect_metrics(self) -> Dict[str, Any]:
        """收集系統指標"""
        # 這裡應該從實際系統收集數據
        metrics = SystemMetrics(
            active_agents=5,
            running_tasks=3,
            queue_depth=10,
            error_rate=0.02,
            response_time_avg=150.0,
            timestamp=datetime.now()
        )
        self.metrics_history.append(metrics)

        return {
            "status": self.system_status.value,
            "metrics": {
                "active_agents": metrics.active_agents,
                "running_tasks": metrics.running_tasks,
                "queue_depth": metrics.queue_depth,
                "error_rate": f"{metrics.error_rate * 100:.2f}%",
                "response_time_avg": f"{metrics.response_time_avg}ms"
            },
            "timestamp": metrics.timestamp.isoformat()
        }

    async def _execute_task(self, task: Dict) -> Dict[str, Any]:
        """執行營運任務"""
        task_type = task.get("type", "")
        target = task.get("target", "")

        # 模擬任務執行
        return {
            "task_id": task.get("id", "unknown"),
            "type": task_type,
            "target": target,
            "status": "completed",
            "message": f"Task {task_type} executed on {target}"
        }

    def _handle_alert(self, alert: Dict) -> Dict[str, Any]:
        """處理告警"""
        alert["received_at"] = datetime.now().isoformat()
        alert["handled_by"] = self.agent_id
        self.alerts.append(alert)

        severity = alert.get("severity", "INFO")

        if severity == "CRITICAL":
            # 緊急告警需要升級
            return {
                "status": "escalated",
                "alert_id": len(self.alerts),
                "message": "Critical alert escalated to NewTaskManager"
            }

        return {
            "status": "acknowledged",
            "alert_id": len(self.alerts),
            "message": f"Alert handled: {alert.get('message', 'No message')}"
        }

    def _generate_report(self, report_type: str) -> Dict[str, Any]:
        """生成報告"""
        if report_type == "status":
            return {
                "report_type": "status",
                "system_status": self.system_status.value,
                "active_alerts": len([a for a in self.alerts if a.get("status") != "resolved"]),
                "metrics_points": len(self.metrics_history),
                "last_metrics": self.metrics_history[-1].__dict__ if self.metrics_history else None
            }
        elif report_type == "daily":
            return {
                "report_type": "daily",
                "date": datetime.now().date().isoformat(),
                "total_alerts": len(self.alerts),
                "metrics_summary": "Daily summary would be here"
            }

        return {"error": f"Unknown report type: {report_type}"}

    async def _health_check(self) -> Dict[str, Any]:
        """系統健康檢查"""
        checks = {
            "message_bus": "healthy",
            "database": "healthy",
            "agents": "healthy",
            "queue": "healthy"
        }

        overall = "HEALTHY"
        for component, status in checks.items():
            if status != "healthy":
                overall = "WARNING"
                break

        return {
            "overall_status": overall,
            "components": checks,
            "timestamp": datetime.now().isoformat()
        }
