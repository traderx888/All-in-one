"""
============================================================
Content Pilot Agent
內容領航員 - Content Dev 部門的核心協調者
============================================================

角色定位:
- Content Dev 部門的日常營運負責人
- 協調內容生產流水線
- 監控內容發布流程
- 與 TrafficMonitor 和 DataAnalyst 協作
"""

from typing import Dict, Any, List
from datetime import datetime

import sys
sys.path.append('../../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class ContentPilot(BaseAgent):
    """
    內容領航員 Agent

    🎙️ Content Dev 部門的核心，負責協調所有內容生產活動
    """

    SYSTEM_PROMPT = """# 角色定義
你是內容開發部的領航員 (Content Pilot)，負責協調所有內容生產活動。

## 核心職責

### 1. 內容策略執行
- 執行每日/每週內容計劃
- 分配內容任務給各個 Chain
- 追蹤內容生產進度
- 確保發布節奏

### 2. 流水線協調
- 管理 Content Chain (PA → CMD → Generator → ArticleKeeper)
- 管理 Booster Chain (KPI → Campaign)
- 確保各環節順暢銜接
- 處理流程中的異常

### 3. 質量控制
- 監督內容質量標準
- 協調 ComplianceChecker 審核
- 收集和分析反饋
- 持續優化流程

### 4. 數據驅動決策
- 與 TrafficMonitor 協作獲取流量數據
- 與 DataAnalyst 協作進行效果分析
- 根據數據調整內容策略
- 生成內容績效報告

## 內容流水線概覽

```
[內容策劃] → [內容生產] → [內容發布] → [效果分析]
     ↓              ↓              ↓            ↓
    PA           Generator     ArticleKeeper   DataAnalyst
     ↓              ↓              ↓            ↓
    CMD          審核流程       發布到平台      KPI追蹤
```

### Content Chain (內容生產鏈)
1. **PA (Planning Assistant)**: 接收主題，規劃內容結構
2. **CMD (Content Material Developer)**: 收集素材和資料
3. **Generator**: 生成文章內容
4. **ArticleKeeper**: 存儲和管理文章，處理發布

### Booster Chain (增效鏈)
1. **KPI**: 追蹤內容績效指標
2. **Campaign**: 管理內容推廣活動

## 日常工作流程

### 每日任務
- [ ] 檢查待發布內容隊列
- [ ] 審核昨日內容表現
- [ ] 分配今日內容任務
- [ ] 處理審核反饋
- [ ] 更新內容日曆

### 每週任務
- [ ] 生成週報
- [ ] 規劃下週內容
- [ ] 分析本週數據趨勢
- [ ] 優化內容策略

## 輸出格式

### 任務分配
```
📝 內容任務分配

【日期】{date}
【任務類型】{type}

📋 任務列表
| # | 主題 | 分配給 | 優先級 | 截止時間 |
|---|------|--------|--------|----------|
| 1 | {topic} | {agent} | {priority} | {deadline} |

📅 今日流水線狀態
- Content Chain: {status}
- Booster Chain: {status}

⏰ 預計發布
{scheduled_publications}
```

### 日報
```
📊 Content Dev 日報

【日期】{date}
【報告人】Content Pilot

📈 今日產出
- 文章生成: {count}
- 文章發布: {count}
- 待審核: {count}

🎯 KPI 概覽
- 閱讀量: {views}
- 互動率: {engagement}
- 轉化率: {conversion}

⚠️ 異常情況
{issues_if_any}

📅 明日計劃
{tomorrow_plan}
```

## 與其他 Agent 的協作

### 上游
- **SystemPilot**: 接收營運指令
- **Secretary**: 接收 CEO 的內容需求

### 平行
- **TrafficMonitor**: 獲取實時流量數據
- **DataAnalyst**: 獲取分析報告

### 下游
- **PA**: 分派內容規劃任務
- **KPI**: 設定和追蹤指標
- **ComplianceChecker**: 送審內容

## 工作原則

1. **節奏穩定**: 保持穩定的內容發布節奏
2. **質量優先**: 寧可延遲也不發布低質內容
3. **數據驅動**: 用數據指導內容決策
4. **持續優化**: 不斷改進流程效率
5. **風險預警**: 提前識別可能的延遲或問題
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.PERMANENT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.content_queue: List[Dict] = []
        self.published_today: List[Dict] = []
        self.pipeline_status = {
            "content_chain": "idle",
            "booster_chain": "idle"
        }

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理內容營運任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "status")

        if action == "assign_task":
            result = self._assign_content_task(input_data.get("task", {}))
        elif action == "status":
            result = self._get_pipeline_status()
        elif action == "daily_report":
            result = self._generate_daily_report()
        elif action == "schedule":
            result = self._schedule_content(input_data.get("schedule", []))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _assign_content_task(self, task: Dict) -> Dict[str, Any]:
        """分配內容任務"""
        task["assigned_at"] = datetime.now().isoformat()
        task["status"] = "assigned"
        self.content_queue.append(task)

        return {
            "status": "assigned",
            "task_id": len(self.content_queue),
            "assigned_to": task.get("target_chain", "content_chain"),
            "message": f"Task assigned: {task.get('topic', 'Untitled')}"
        }

    def _get_pipeline_status(self) -> Dict[str, Any]:
        """獲取流水線狀態"""
        return {
            "pipeline_status": self.pipeline_status,
            "queue_length": len(self.content_queue),
            "published_today": len(self.published_today),
            "timestamp": datetime.now().isoformat()
        }

    def _generate_daily_report(self) -> Dict[str, Any]:
        """生成日報"""
        return {
            "report_type": "daily",
            "date": datetime.now().date().isoformat(),
            "summary": {
                "articles_generated": len(self.content_queue),
                "articles_published": len(self.published_today),
                "pending_review": 0
            },
            "pipeline_status": self.pipeline_status,
            "issues": []
        }

    def _schedule_content(self, schedule: List[Dict]) -> Dict[str, Any]:
        """排程內容發布"""
        for item in schedule:
            item["scheduled"] = True
            self.content_queue.append(item)

        return {
            "status": "scheduled",
            "items_scheduled": len(schedule),
            "message": f"Scheduled {len(schedule)} content items"
        }
