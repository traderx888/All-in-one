"""
============================================================
Traffic Monitor Agent
流量監控員 - 實時追蹤內容表現
============================================================
"""

from typing import Dict, Any, List
from datetime import datetime

import sys
sys.path.append('../../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class TrafficMonitor(BaseAgent):
    """
    流量監控員 Agent

    📊 負責監控所有內容的流量和互動數據
    """

    SYSTEM_PROMPT = """# 角色定義
你是內容開發部的流量監控員 (Traffic Monitor)，負責實時追蹤內容表現。

## 核心職責

### 1. 流量監控
- 實時監控各平台流量
- 追蹤頁面瀏覽量
- 監測訪客來源
- 識別流量異常

### 2. 互動追蹤
- 監控用戶互動行為
- 追蹤評論和分享
- 分析停留時間
- 監測跳出率

### 3. 告警管理
- 設定流量閾值
- 發送異常告警
- 識別熱門內容
- 預警流量下降

### 4. 數據匯報
- 生成實時數據報告
- 提供給 Content Pilot 決策參考
- 與 DataAnalyst 共享數據
- 記錄歷史趨勢

## 監控指標

### 流量指標
- Page Views (PV): 頁面瀏覽量
- Unique Visitors (UV): 獨立訪客
- Sessions: 會話數
- Traffic Sources: 流量來源

### 互動指標
- Engagement Rate: 互動率
- Bounce Rate: 跳出率
- Time on Page: 頁面停留時間
- Scroll Depth: 滾動深度

### 轉化指標
- Click-through Rate (CTR): 點擊率
- Conversion Rate: 轉化率
- Social Shares: 社交分享

## 輸出格式

### 實時數據
```
📈 流量實時數據

【更新時間】{timestamp}

🔢 當前指標
- 實時訪客: {realtime_visitors}
- 今日 PV: {today_pv}
- 今日 UV: {today_uv}

📊 熱門內容 (過去 1 小時)
| 排名 | 標題 | PV | 來源 |
|------|------|-----|------|
| 1 | {title} | {pv} | {source} |

⚠️ 告警
{alerts_if_any}
```

## 與其他 Agent 的協作

- **Content Pilot**: 提供流量數據支持決策
- **DataAnalyst**: 共享原始數據進行深度分析
- **KPI**: 提供數據用於 KPI 計算
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.PERMANENT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.metrics_cache: Dict[str, Any] = {}
        self.alerts: List[Dict] = []

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理流量監控任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "get_realtime")

        if action == "get_realtime":
            result = self._get_realtime_metrics()
        elif action == "get_content_stats":
            result = self._get_content_stats(input_data.get("content_id"))
        elif action == "set_alert":
            result = self._set_alert(input_data.get("alert_config", {}))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _get_realtime_metrics(self) -> Dict[str, Any]:
        """獲取實時指標"""
        return {
            "timestamp": datetime.now().isoformat(),
            "realtime_visitors": 42,
            "today_pv": 1250,
            "today_uv": 380,
            "top_content": [
                {"title": "Sample Article 1", "pv": 150, "source": "organic"},
                {"title": "Sample Article 2", "pv": 120, "source": "social"}
            ],
            "alerts": self.alerts[-5:] if self.alerts else []
        }

    def _get_content_stats(self, content_id: str) -> Dict[str, Any]:
        """獲取特定內容的統計"""
        return {
            "content_id": content_id,
            "pv": 500,
            "uv": 320,
            "avg_time_on_page": 180,
            "bounce_rate": 0.35,
            "engagement_rate": 0.12
        }

    def _set_alert(self, config: Dict) -> Dict[str, Any]:
        """設置告警"""
        self.alerts.append({
            "config": config,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        })
        return {"status": "alert_set", "alert_id": len(self.alerts)}
