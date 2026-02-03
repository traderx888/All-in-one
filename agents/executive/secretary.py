"""
============================================================
Secretary Agent (CEO 秘書)
意圖路由器 - CEO 的第一道關口
============================================================

角色定位:
- 作為 CEO 與整個組織的唯一接口
- 理解 CEO 的全域需求
- 將指令精確轉發給管理中樞
- 整合各部門回報，形成簡潔報告

工作流程:
1. 接收 CEO 指令
2. 解析意圖，判斷任務類型
3. 路由到適當的管理區域 (ARD/LAW)
4. 追蹤任務進度
5. 彙整報告回覆 CEO
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

import sys
sys.path.append('../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class IntentType(Enum):
    """意圖類型"""
    DEVELOPMENT = "development"      # 開發新功能/Agent
    OPERATION = "operation"          # 日常營運任務
    COMPLIANCE = "compliance"        # 合規審計相關
    INFORMATION = "information"      # 查詢信息
    REPORT = "report"               # 生成報告
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    """解析後的意圖"""
    type: IntentType
    target_zone: str              # ARD, LAW, ContentDev, ProductDev, TradingDev
    target_agents: List[str]      # 具體目標 agent
    priority: int                 # 1-10
    summary: str                  # 意圖摘要
    original_request: str         # 原始請求


class Secretary(BaseAgent):
    """
    CEO 秘書 Agent

    🎧 作為意圖路由器，是 CEO 與 AI 組織之間的橋樑
    """

    SYSTEM_PROMPT = """# 角色定義
你是 CEO 的 AI 秘書 (Secretary)，代號「Secy」。

## 核心職責
1. **意圖理解**: 精確理解 CEO 的每一個指令背後的真實意圖
2. **智能路由**: 將任務分發到正確的管理區域和執行部門
3. **進度追蹤**: 持續追蹤所有進行中的任務狀態
4. **報告彙整**: 將各部門的回報整合成簡潔的執行摘要

## 組織架構認知

### 管理中樞 (Management Hub)
- **Zone ARD** (Agent Resource Development):
  - SystemPilot: 系統運行監控，營運模式的主要執行者
  - NewTaskManager: 新任務分配，開發模式的協調者
  - DatabaseChecker: 數據庫狀態檢查
  - MasterArchitect: 架構設計，負責解構和設計新 Agent

- **Zone LAW** (Law & Compliance):
  - ComplianceChecker: 合規檢查，確保所有輸出符合規範

### 執行部門
- **Content Dev**: 內容開發部，半流水線模式運行
- **Product Dev**: 產品開發部，動態團隊模式
- **Trading Dev**: 交易開發部，動態團隊模式

## 意圖分類規則

### 開發類 (→ ARD.NewTaskManager)
關鍵詞: 建立、創建、新增、開發、設計、架構、重構
示例: "建立一個新的監控 Agent"、"設計交易策略模組"

### 營運類 (→ ARD.SystemPilot)
關鍵詞: 執行、運行、啟動、監控、檢查、日常、更新
示例: "執行每日內容更新"、"啟動交易監控"

### 合規類 (→ LAW.ComplianceChecker)
關鍵詞: 審核、合規、檢查、規範、安全、審計
示例: "審核這篇文章的合規性"、"檢查代碼安全性"

### 查詢類 (→ Librarian)
關鍵詞: 查詢、搜索、找、什麼是、如何、狀態
示例: "查詢上週的營收數據"、"找到相關的技術文檔"

## 輸出格式

當分析完 CEO 的指令後，回覆格式如下:

```
📋 意圖分析報告

【原始指令】
{CEO 的原始輸入}

【意圖類型】
{DEVELOPMENT/OPERATION/COMPLIANCE/INFORMATION/REPORT}

【路由決策】
- 主要目標: {Zone/Department}
- 執行 Agent: {具體 Agent 列表}
- 優先級: {1-10}

【任務摘要】
{一句話描述這個任務的核心目標}

【執行計劃】
1. {步驟1}
2. {步驟2}
...

【預期交付】
{描述任務完成後應該產出什麼}
```

## 工作原則

1. **精確不猜測**: 如果意圖不明確，詢問而非假設
2. **高效路由**: 選擇最直接的路徑，避免不必要的中間層
3. **優先級判斷**: 緊急任務標記高優先級，確保及時處理
4. **信息完整**: 轉發任務時包含所有必要上下文
5. **狀態透明**: 主動報告任務進度，不讓 CEO 等待

## 特殊指令

- `status`: 報告所有進行中任務的狀態
- `report`: 生成當日工作摘要
- `escalate`: 將問題升級，需要 CEO 直接介入
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.PERMANENT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.active_tasks: Dict[str, Dict] = {}
        self.intent_history: List[ParsedIntent] = []

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理 CEO 輸入

        Args:
            input_data: {
                "message": str,        # CEO 的指令
                "context": dict,       # 可選的上下文信息
                "priority_override": int  # 可選的優先級覆蓋
            }

        Returns:
            {
                "parsed_intent": ParsedIntent,
                "routing_decision": dict,
                "response": str
            }
        """
        self.update_status(AgentStatus.BUSY)

        message = input_data.get("message", "")
        context = input_data.get("context", {})

        # 解析意圖
        parsed_intent = self._parse_intent(message)
        self.intent_history.append(parsed_intent)

        # 生成路由決策
        routing = self._generate_routing(parsed_intent)

        # 創建任務追蹤
        task_id = f"task_{len(self.active_tasks) + 1}"
        self.active_tasks[task_id] = {
            "intent": parsed_intent,
            "routing": routing,
            "status": "pending",
            "created_at": "now"
        }

        self.update_status(AgentStatus.IDLE)

        return {
            "task_id": task_id,
            "parsed_intent": parsed_intent,
            "routing_decision": routing,
            "response": self._format_response(parsed_intent, routing)
        }

    def _parse_intent(self, message: str) -> ParsedIntent:
        """解析意圖 (簡化版，實際應調用 LLM)"""
        message_lower = message.lower()

        # 關鍵詞匹配
        dev_keywords = ['建立', '創建', '新增', '開發', '設計', '架構', 'create', 'build', 'develop']
        ops_keywords = ['執行', '運行', '啟動', '監控', '檢查', 'run', 'execute', 'monitor']
        compliance_keywords = ['審核', '合規', '規範', '安全', 'audit', 'compliance']
        query_keywords = ['查詢', '搜索', '找', '什麼', '如何', 'search', 'find', 'what', 'how']

        intent_type = IntentType.UNKNOWN
        target_zone = "ARD"
        target_agents = ["NewTaskManager"]

        if any(kw in message_lower for kw in dev_keywords):
            intent_type = IntentType.DEVELOPMENT
            target_zone = "ARD"
            target_agents = ["NewTaskManager", "MasterArchitect"]
        elif any(kw in message_lower for kw in ops_keywords):
            intent_type = IntentType.OPERATION
            target_zone = "ARD"
            target_agents = ["SystemPilot"]
        elif any(kw in message_lower for kw in compliance_keywords):
            intent_type = IntentType.COMPLIANCE
            target_zone = "LAW"
            target_agents = ["ComplianceChecker"]
        elif any(kw in message_lower for kw in query_keywords):
            intent_type = IntentType.INFORMATION
            target_zone = "Library"
            target_agents = ["Librarian"]

        return ParsedIntent(
            type=intent_type,
            target_zone=target_zone,
            target_agents=target_agents,
            priority=5,
            summary=f"任務: {message[:50]}...",
            original_request=message
        )

    def _generate_routing(self, intent: ParsedIntent) -> Dict[str, Any]:
        """生成路由決策"""
        return {
            "primary_route": intent.target_zone,
            "agents": intent.target_agents,
            "fallback_route": "ARD.NewTaskManager",
            "requires_approval": intent.target_zone in ["ProductDev", "TradingDev"],
            "priority": intent.priority
        }

    def _format_response(self, intent: ParsedIntent, routing: Dict) -> str:
        """格式化回覆"""
        return f"""📋 意圖分析報告

【原始指令】
{intent.original_request}

【意圖類型】
{intent.type.value.upper()}

【路由決策】
- 主要目標: {routing['primary_route']}
- 執行 Agent: {', '.join(routing['agents'])}
- 優先級: {routing['priority']}/10

【任務摘要】
{intent.summary}

【狀態】
✅ 任務已路由，等待執行部門回覆
"""
