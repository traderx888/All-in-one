"""
============================================================
Database Checker Agent
數據庫檢查員 - 數據層的守護者
============================================================

角色定位:
- 監控數據庫健康狀態
- 驗證數據完整性
- 執行數據遷移檢查
- 提供數據查詢服務

工作範圍:
- 知識庫 (Librarian 管理)
- 任務數據庫
- 用戶數據
- 交易數據
- 內容數據
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

import sys
sys.path.append('../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class DatabaseHealth(Enum):
    """數據庫健康狀態"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"


@dataclass
class DatabaseMetrics:
    """數據庫指標"""
    name: str
    size_mb: float
    record_count: int
    last_backup: datetime
    health: DatabaseHealth
    response_time_ms: float


class DatabaseChecker(BaseAgent):
    """
    數據庫檢查員 Agent

    🗄️ 負責數據層的監控、驗證和維護
    """

    SYSTEM_PROMPT = """# 角色定義
你是 AI 組織的數據庫檢查員 (DatabaseChecker)，Zone ARD 的數據層守護者。

## 核心職責

### 1. 數據庫監控
- 監控各數據庫的健康狀態
- 追蹤存儲使用情況
- 監測查詢性能
- 識別潛在問題

### 2. 數據完整性驗證
- 驗證數據結構正確性
- 檢查外鍵約束
- 識別孤立記錄
- 驗證數據一致性

### 3. 備份與恢復
- 監控備份任務狀態
- 驗證備份完整性
- 協助數據恢復
- 管理備份策略

### 4. 數據遷移
- 評估遷移可行性
- 驗證遷移前後數據
- 監控遷移進度
- 報告遷移結果

## 監控的數據庫

### 1. Knowledge Base (知識庫)
- 管理者: Librarian
- 內容: 技術文檔、業務規範、歷史記錄
- 重要性: 高

### 2. Task Database (任務數據庫)
- 管理者: NewTaskManager
- 內容: 任務定義、執行記錄、狀態追蹤
- 重要性: 高

### 3. Content Database (內容數據庫)
- 管理者: Content Dev
- 內容: 文章、媒體資源、發布記錄
- 重要性: 中

### 4. Trading Database (交易數據庫)
- 管理者: Trading Dev
- 內容: 交易記錄、策略配置、市場數據
- 重要性: 極高

### 5. User Database (用戶數據庫)
- 管理者: System
- 內容: 用戶配置、權限設定
- 重要性: 高

## 健康檢查清單

### 每小時
- [ ] 連接性測試
- [ ] 響應時間檢查
- [ ] 錯誤日誌掃描

### 每日
- [ ] 存儲空間檢查
- [ ] 備份狀態驗證
- [ ] 性能指標分析
- [ ] 異常記錄審查

### 每週
- [ ] 完整性掃描
- [ ] 索引優化分析
- [ ] 歷史數據歸檔
- [ ] 容量規劃評估

## 輸出格式

### 健康報告
```
🗄️ 數據庫健康報告

【檢查時間】{timestamp}
【整體狀態】{HEALTHY/DEGRADED/CRITICAL}

📊 數據庫狀態
| 數據庫 | 狀態 | 大小 | 記錄數 | 響應時間 |
|--------|------|------|--------|----------|
| {name} | {status} | {size}MB | {records} | {time}ms |

💾 備份狀態
| 數據庫 | 最後備份 | 備份大小 | 狀態 |
|--------|----------|----------|------|
| {name} | {time} | {size}MB | {ok/warning} |

⚠️ 告警 (如有)
{告警列表}

📝 建議
{優化建議}
```

### 完整性報告
```
✅ 數據完整性報告

【數據庫】{database_name}
【檢查時間】{timestamp}

🔍 檢查結果
- 結構驗證: {PASS/FAIL}
- 約束檢查: {PASS/FAIL}
- 一致性檢查: {PASS/FAIL}
- 孤立記錄: {count}

📋 詳細發現
{具體問題描述}

🔧 修復建議
{修復方案}
```

## 告警閾值

### 存儲空間
- 🟢 正常: < 70%
- 🟡 警告: 70-85%
- 🔴 緊急: > 85%

### 響應時間
- 🟢 正常: < 100ms
- 🟡 警告: 100-500ms
- 🔴 緊急: > 500ms

### 備份年齡
- 🟢 正常: < 24h
- 🟡 警告: 24-48h
- 🔴 緊急: > 48h

## 工作原則

1. **數據安全第一**: 永遠不要冒險操作生產數據
2. **定期驗證**: 不要假設數據是正確的
3. **備份優先**: 任何修改前確保有可用備份
4. **詳細記錄**: 所有操作都要有日誌
5. **及時告警**: 問題發現後立即通知

## 與其他 Agent 的協作

- **SystemPilot**: 報告數據庫健康狀態
- **NewTaskManager**: 提供任務數據查詢
- **Librarian**: 協助知識庫維護
- **ComplianceChecker**: 提供數據合規報告
- **各部門**: 支援部門數據需求
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.PERMANENT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.databases: Dict[str, DatabaseMetrics] = {}
        self.health_history: List[Dict] = []
        self.alerts: List[Dict] = []

        # 初始化模擬數據庫
        self._init_mock_databases()

    def _init_mock_databases(self):
        """初始化模擬數據庫數據"""
        now = datetime.now()
        self.databases = {
            "knowledge_base": DatabaseMetrics(
                name="knowledge_base",
                size_mb=256.5,
                record_count=1500,
                last_backup=now,
                health=DatabaseHealth.HEALTHY,
                response_time_ms=45.0
            ),
            "task_db": DatabaseMetrics(
                name="task_db",
                size_mb=128.0,
                record_count=5000,
                last_backup=now,
                health=DatabaseHealth.HEALTHY,
                response_time_ms=32.0
            ),
            "content_db": DatabaseMetrics(
                name="content_db",
                size_mb=512.0,
                record_count=3000,
                last_backup=now,
                health=DatabaseHealth.HEALTHY,
                response_time_ms=55.0
            ),
            "trading_db": DatabaseMetrics(
                name="trading_db",
                size_mb=1024.0,
                record_count=100000,
                last_backup=now,
                health=DatabaseHealth.HEALTHY,
                response_time_ms=28.0
            )
        }

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理數據庫相關請求

        Args:
            input_data: {
                "action": str,        # health_check, integrity_check, query, backup_status
                "database": str,      # 目標數據庫
                "params": dict        # 額外參數
            }

        Returns:
            處理結果
        """
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "health_check")
        database = input_data.get("database")

        if action == "health_check":
            result = self._health_check(database)
        elif action == "integrity_check":
            result = self._integrity_check(database)
        elif action == "query":
            result = self._execute_query(database, input_data.get("params", {}))
        elif action == "backup_status":
            result = self._check_backup_status(database)
        elif action == "full_report":
            result = self._generate_full_report()
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _health_check(self, database: Optional[str] = None) -> Dict[str, Any]:
        """執行健康檢查"""
        if database and database in self.databases:
            dbs = {database: self.databases[database]}
        else:
            dbs = self.databases

        results = {}
        overall_health = "HEALTHY"

        for name, metrics in dbs.items():
            status = {
                "health": metrics.health.value,
                "size_mb": metrics.size_mb,
                "record_count": metrics.record_count,
                "response_time_ms": metrics.response_time_ms,
                "last_backup": metrics.last_backup.isoformat()
            }
            results[name] = status

            if metrics.health != DatabaseHealth.HEALTHY:
                overall_health = "DEGRADED"
            if metrics.health == DatabaseHealth.CRITICAL:
                overall_health = "CRITICAL"

        check_result = {
            "overall_health": overall_health,
            "databases": results,
            "checked_at": datetime.now().isoformat()
        }

        self.health_history.append(check_result)
        return check_result

    def _integrity_check(self, database: str) -> Dict[str, Any]:
        """執行完整性檢查"""
        if database not in self.databases:
            return {"error": f"Database not found: {database}"}

        # 模擬完整性檢查
        return {
            "database": database,
            "checks": {
                "structure_valid": True,
                "constraints_ok": True,
                "consistency_ok": True,
                "orphan_records": 0
            },
            "status": "PASS",
            "checked_at": datetime.now().isoformat()
        }

    def _execute_query(self, database: str, params: Dict) -> Dict[str, Any]:
        """執行數據查詢"""
        if database not in self.databases:
            return {"error": f"Database not found: {database}"}

        query_type = params.get("type", "count")

        if query_type == "count":
            return {
                "database": database,
                "record_count": self.databases[database].record_count
            }
        elif query_type == "size":
            return {
                "database": database,
                "size_mb": self.databases[database].size_mb
            }

        return {"error": f"Unknown query type: {query_type}"}

    def _check_backup_status(self, database: Optional[str] = None) -> Dict[str, Any]:
        """檢查備份狀態"""
        if database and database in self.databases:
            dbs = {database: self.databases[database]}
        else:
            dbs = self.databases

        results = {}
        for name, metrics in dbs.items():
            age_hours = (datetime.now() - metrics.last_backup).total_seconds() / 3600
            status = "OK" if age_hours < 24 else "WARNING" if age_hours < 48 else "CRITICAL"

            results[name] = {
                "last_backup": metrics.last_backup.isoformat(),
                "age_hours": round(age_hours, 2),
                "status": status
            }

        return {
            "backup_status": results,
            "checked_at": datetime.now().isoformat()
        }

    def _generate_full_report(self) -> Dict[str, Any]:
        """生成完整報告"""
        return {
            "health": self._health_check(),
            "backups": self._check_backup_status(),
            "summary": {
                "total_databases": len(self.databases),
                "total_size_mb": sum(db.size_mb for db in self.databases.values()),
                "total_records": sum(db.record_count for db in self.databases.values())
            },
            "generated_at": datetime.now().isoformat()
        }
