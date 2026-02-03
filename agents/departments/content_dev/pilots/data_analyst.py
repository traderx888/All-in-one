"""
============================================================
Data Analyst Agent
數據分析師 - 深度分析內容效果
============================================================
"""

from typing import Dict, Any, List
from datetime import datetime

import sys
sys.path.append('../../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class DataAnalyst(BaseAgent):
    """
    數據分析師 Agent

    📉 負責深度分析內容表現，提供策略建議
    """

    SYSTEM_PROMPT = """# 角色定義
你是內容開發部的數據分析師 (Data Analyst)，負責深度分析內容效果。

## 核心職責

### 1. 數據分析
- 分析內容表現數據
- 識別趨勢和模式
- 進行同期比較
- 評估內容ROI

### 2. 洞察生成
- 識別高表現內容特徵
- 分析受眾行為
- 發現增長機會
- 提供優化建議

### 3. 報告生成
- 製作週報/月報
- 創建數據儀表板
- 視覺化關鍵指標
- 追蹤長期趨勢

### 4. 策略支持
- 為內容策略提供數據支持
- A/B 測試分析
- 預測模型構建
- ROI 評估

## 分析框架

### 內容表現分析
1. 流量維度: PV, UV, 來源分布
2. 互動維度: 互動率, 評論, 分享
3. 轉化維度: CTR, 轉化率, 收益
4. 時間維度: 趨勢, 週期性, 生命週期

### 受眾分析
1. 人口統計: 年齡, 地區, 設備
2. 行為特徵: 訪問頻率, 停留時長
3. 興趣偏好: 內容類型, 閱讀習慣
4. 轉化路徑: 接觸點, 決策過程

## 輸出格式

### 分析報告
```
📊 內容分析報告

【報告類型】{type}
【分析期間】{period}
【生成時間】{timestamp}

📈 關鍵發現
1. {finding_1}
2. {finding_2}

📉 數據摘要
| 指標 | 本期 | 上期 | 變化 |
|------|------|------|------|
| {metric} | {current} | {previous} | {change}% |

🎯 建議行動
1. {recommendation_1}
2. {recommendation_2}

📝 詳細分析
{detailed_analysis}
```

## 與其他 Agent 的協作

- **Content Pilot**: 提供分析結果支持決策
- **TrafficMonitor**: 獲取原始流量數據
- **KPI**: 協作制定和評估KPI
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.PERMANENT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.analysis_history: List[Dict] = []

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理數據分析任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "analyze")

        if action == "analyze":
            result = self._analyze_content_performance(input_data.get("params", {}))
        elif action == "generate_report":
            result = self._generate_report(input_data.get("report_type", "weekly"))
        elif action == "get_insights":
            result = self._get_insights(input_data.get("topic"))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _analyze_content_performance(self, params: Dict) -> Dict[str, Any]:
        """分析內容表現"""
        return {
            "analysis_type": "content_performance",
            "period": params.get("period", "last_7_days"),
            "summary": {
                "total_articles": 15,
                "total_views": 25000,
                "avg_engagement": 0.08,
                "top_performer": "Article about AI trends"
            },
            "trends": {
                "views_trend": "+15%",
                "engagement_trend": "+5%"
            },
            "recommendations": [
                "增加 AI 相關主題的內容",
                "優化文章標題以提高 CTR"
            ]
        }

    def _generate_report(self, report_type: str) -> Dict[str, Any]:
        """生成報告"""
        report = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "metrics": {
                "pv": {"current": 25000, "previous": 22000, "change": 13.6},
                "uv": {"current": 8000, "previous": 7500, "change": 6.7},
                "engagement_rate": {"current": 0.08, "previous": 0.075, "change": 6.7}
            },
            "key_findings": [
                "整體流量較上期增長 13.6%",
                "互動率持續改善",
                "社交媒體成為主要流量來源"
            ],
            "action_items": [
                "加強社交媒體內容投放",
                "優化 SEO 策略"
            ]
        }
        self.analysis_history.append(report)
        return report

    def _get_insights(self, topic: str) -> Dict[str, Any]:
        """獲取洞察"""
        return {
            "topic": topic,
            "insights": [
                {"type": "trend", "description": "AI 相關內容需求上升"},
                {"type": "opportunity", "description": "技術教程類內容缺口"},
                {"type": "risk", "description": "競爭對手內容量增加"}
            ]
        }
