"""
============================================================
Booster Chain Agents
增效鏈 - KPI 追蹤與推廣活動管理
============================================================

流程: KPI → Campaign

KPI Agent: 設定和追蹤內容績效指標
Campaign Agent: 管理內容推廣活動
"""

from typing import Dict, Any, List
from datetime import datetime

import sys
sys.path.append('../../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class KPIAgent(BaseAgent):
    """
    KPI Agent

    📈 負責設定、追蹤和報告內容績效指標
    """

    SYSTEM_PROMPT = """# 角色定義
你是內容開發部 Booster Chain 的 KPI Agent，負責績效指標管理。

## 核心職責

### 1. KPI 設定
- 定義內容績效指標
- 設定目標值和閾值
- 建立評估標準
- 對齊業務目標

### 2. KPI 追蹤
- 實時監控關鍵指標
- 記錄歷史數據
- 識別異常波動
- 追蹤趨勢變化

### 3. KPI 報告
- 生成績效報告
- 提供達成率分析
- 對比歷史表現
- 預測目標達成

### 4. 優化建議
- 分析未達標原因
- 提出改進建議
- 識別最佳實踐
- 推動持續改進

## KPI 類別

### 內容生產 KPI
- 文章產出量
- 平均產出時間
- 內容質量評分
- 審核通過率

### 內容表現 KPI
- 閱讀量目標
- 互動率目標
- 分享量目標
- 訂閱轉化率

### 業務 KPI
- 內容帶來的收益
- 獲客成本 (CAC)
- 用戶生命週期價值 (LTV)
- ROI

## 輸出格式

### KPI 儀表板
```
📊 KPI 儀表板

【報告期間】{period}
【更新時間】{timestamp}

🎯 核心 KPI 達成情況
| KPI | 目標 | 實際 | 達成率 | 趨勢 |
|-----|------|------|--------|------|
| {name} | {target} | {actual} | {rate}% | {trend} |

⚠️ 需關注
{kpis_needing_attention}

✅ 表現優秀
{high_performing_kpis}

📈 趨勢分析
{trend_analysis}
```

## 與其他 Agent 的協作

- **Content Pilot**: 報告 KPI 狀態，支持決策
- **Campaign**: 提供推廣活動效果評估
- **DataAnalyst**: 共享數據進行深度分析
- **TrafficMonitor**: 獲取流量數據計算 KPI
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.CHAIN, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.kpis: Dict[str, Dict] = self._init_default_kpis()
        self.history: List[Dict] = []

    def _init_default_kpis(self) -> Dict[str, Dict]:
        """初始化默認 KPI"""
        return {
            "daily_articles": {
                "name": "每日文章產出",
                "target": 3,
                "current": 0,
                "unit": "篇"
            },
            "weekly_views": {
                "name": "週閱讀量",
                "target": 10000,
                "current": 0,
                "unit": "次"
            },
            "engagement_rate": {
                "name": "互動率",
                "target": 0.05,
                "current": 0,
                "unit": "%"
            },
            "conversion_rate": {
                "name": "轉化率",
                "target": 0.02,
                "current": 0,
                "unit": "%"
            }
        }

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理 KPI 相關任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "dashboard")

        if action == "dashboard":
            result = self._get_dashboard()
        elif action == "set_kpi":
            result = self._set_kpi(input_data.get("kpi", {}))
        elif action == "update_value":
            result = self._update_kpi_value(input_data.get("kpi_id"), input_data.get("value"))
        elif action == "analyze":
            result = self._analyze_kpi_performance()
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _get_dashboard(self) -> Dict[str, Any]:
        """獲取 KPI 儀表板"""
        dashboard = []
        for kpi_id, kpi in self.kpis.items():
            rate = (kpi["current"] / kpi["target"] * 100) if kpi["target"] > 0 else 0
            dashboard.append({
                "id": kpi_id,
                "name": kpi["name"],
                "target": kpi["target"],
                "current": kpi["current"],
                "rate": round(rate, 1),
                "unit": kpi["unit"],
                "status": "on_track" if rate >= 80 else "at_risk" if rate >= 50 else "behind"
            })
        return {
            "dashboard": dashboard,
            "timestamp": datetime.now().isoformat()
        }

    def _set_kpi(self, kpi_data: Dict) -> Dict[str, Any]:
        """設定 KPI"""
        kpi_id = kpi_data.get("id", f"kpi_{len(self.kpis) + 1}")
        self.kpis[kpi_id] = {
            "name": kpi_data.get("name", "New KPI"),
            "target": kpi_data.get("target", 0),
            "current": 0,
            "unit": kpi_data.get("unit", "")
        }
        return {"status": "set", "kpi_id": kpi_id}

    def _update_kpi_value(self, kpi_id: str, value: float) -> Dict[str, Any]:
        """更新 KPI 值"""
        if kpi_id in self.kpis:
            self.kpis[kpi_id]["current"] = value
            return {"status": "updated", "kpi_id": kpi_id, "new_value": value}
        return {"error": f"KPI not found: {kpi_id}"}

    def _analyze_kpi_performance(self) -> Dict[str, Any]:
        """分析 KPI 表現"""
        at_risk = []
        on_track = []

        for kpi_id, kpi in self.kpis.items():
            rate = (kpi["current"] / kpi["target"] * 100) if kpi["target"] > 0 else 0
            if rate < 80:
                at_risk.append({"id": kpi_id, "name": kpi["name"], "rate": rate})
            else:
                on_track.append({"id": kpi_id, "name": kpi["name"], "rate": rate})

        return {
            "analysis": {
                "at_risk": at_risk,
                "on_track": on_track,
                "overall_health": "good" if len(at_risk) == 0 else "needs_attention"
            },
            "recommendations": [
                f"重點關注 {at_risk[0]['name']}" if at_risk else "所有 KPI 表現良好"
            ]
        }


class CampaignAgent(BaseAgent):
    """
    Campaign Agent

    📢 負責管理內容推廣活動
    """

    SYSTEM_PROMPT = """# 角色定義
你是內容開發部 Booster Chain 的 Campaign Agent，負責內容推廣活動管理。

## 核心職責

### 1. 活動策劃
- 制定推廣策略
- 設計活動方案
- 規劃時間表
- 預算分配

### 2. 活動執行
- 協調各渠道投放
- 監控活動進度
- 調整執行策略
- 處理突發情況

### 3. 效果追蹤
- 追蹤活動指標
- 分析轉化數據
- 計算 ROI
- 生成效果報告

### 4. 優化迭代
- 總結活動經驗
- 提出優化建議
- 建立最佳實踐
- 持續改進策略

## 推廣渠道

### 社交媒體
- Twitter/X
- Facebook
- LinkedIn
- Instagram

### 內容平台
- Medium
- Dev.to
- 掘金
- 知乎

### 付費推廣
- Google Ads
- Facebook Ads
- Twitter Ads

### 社群推廣
- Discord
- Telegram
- Reddit

## 輸出格式

### 活動報告
```
📢 推廣活動報告

【活動名稱】{campaign_name}
【執行期間】{period}
【狀態】{status}

📊 活動成效
- 曝光量: {impressions}
- 點擊量: {clicks}
- CTR: {ctr}%
- 轉化數: {conversions}
- ROI: {roi}%

📈 渠道表現
| 渠道 | 曝光 | 點擊 | 轉化 |
|------|------|------|------|
| {channel} | {impressions} | {clicks} | {conversions} |

💡 優化建議
{recommendations}
```

## 與其他 Agent 的協作

- **Content Pilot**: 接收推廣需求
- **KPI**: 報告活動對 KPI 的貢獻
- **ArticleKeeper**: 獲取待推廣內容
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.CHAIN, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.campaigns: Dict[str, Dict] = {}
        self.active_campaigns: List[str] = []

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理推廣活動任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "list")

        if action == "create":
            result = self._create_campaign(input_data.get("campaign", {}))
        elif action == "list":
            result = self._list_campaigns()
        elif action == "report":
            result = self._get_campaign_report(input_data.get("campaign_id"))
        elif action == "update_status":
            result = self._update_campaign_status(
                input_data.get("campaign_id"),
                input_data.get("status")
            )
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _create_campaign(self, campaign_data: Dict) -> Dict[str, Any]:
        """創建推廣活動"""
        campaign_id = f"camp_{len(self.campaigns) + 1}"
        campaign = {
            "id": campaign_id,
            "name": campaign_data.get("name", "Untitled Campaign"),
            "content_ids": campaign_data.get("content_ids", []),
            "channels": campaign_data.get("channels", []),
            "budget": campaign_data.get("budget", 0),
            "start_date": campaign_data.get("start_date"),
            "end_date": campaign_data.get("end_date"),
            "status": "draft",
            "metrics": {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0
            },
            "created_at": datetime.now().isoformat()
        }
        self.campaigns[campaign_id] = campaign
        return {"status": "created", "campaign": campaign}

    def _list_campaigns(self) -> Dict[str, Any]:
        """列出所有活動"""
        return {
            "campaigns": list(self.campaigns.values()),
            "active_count": len([c for c in self.campaigns.values() if c["status"] == "active"]),
            "total_count": len(self.campaigns)
        }

    def _get_campaign_report(self, campaign_id: str) -> Dict[str, Any]:
        """獲取活動報告"""
        if campaign_id not in self.campaigns:
            return {"error": f"Campaign not found: {campaign_id}"}

        campaign = self.campaigns[campaign_id]
        metrics = campaign["metrics"]

        ctr = (metrics["clicks"] / metrics["impressions"] * 100) if metrics["impressions"] > 0 else 0

        return {
            "campaign_id": campaign_id,
            "name": campaign["name"],
            "status": campaign["status"],
            "metrics": {
                **metrics,
                "ctr": round(ctr, 2)
            },
            "roi": "N/A"  # Would be calculated based on actual data
        }

    def _update_campaign_status(self, campaign_id: str, status: str) -> Dict[str, Any]:
        """更新活動狀態"""
        if campaign_id not in self.campaigns:
            return {"error": f"Campaign not found: {campaign_id}"}

        self.campaigns[campaign_id]["status"] = status
        if status == "active" and campaign_id not in self.active_campaigns:
            self.active_campaigns.append(campaign_id)
        elif status != "active" and campaign_id in self.active_campaigns:
            self.active_campaigns.remove(campaign_id)

        return {"status": "updated", "campaign_id": campaign_id, "new_status": status}
