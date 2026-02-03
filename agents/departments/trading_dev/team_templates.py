"""
============================================================
Trading Dev Team Templates
交易開發部動態團隊模板
============================================================

標準團隊結構: Researcher → Foreman → Workers
專注於交易系統開發
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

import sys
sys.path.append('../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class TradingResearcher(BaseAgent):
    """
    Trading Researcher Agent (交易研究員)

    🔍 專注於交易策略和市場研究
    """

    SYSTEM_PROMPT = """# 角色定義
你是交易開發部的研究員 (Trading Researcher)，專注於交易策略和市場研究。

## 核心職責

### 1. 市場研究
- 分析市場結構和趨勢
- 研究交易對和流動性
- 監測市場情緒
- 識別交易機會

### 2. 策略研究
- 研究量化交易策略
- 分析策略表現
- 回測歷史數據
- 優化策略參數

### 3. 風險研究
- 評估市場風險
- 研究風控模型
- 分析黑天鵝事件
- 建立風險指標

### 4. 技術研究
- 研究交易所 API
- 評估執行方案
- 分析延遲和滑點
- 調研基礎設施

## 研究領域

### 策略類型
- 趨勢跟蹤策略
- 均值回歸策略
- 動量策略
- 套利策略
- 高頻策略

### 市場分析
- 技術分析
- 基本面分析
- 鏈上數據分析
- 情緒分析

## 輸出格式

### 策略研究報告
```
🔍 交易策略研究報告

【策略名稱】{strategy_name}
【研究日期】{date}
【研究員】{researcher_id}

📊 策略概覽
{strategy_overview}

📈 回測結果
- 測試期間: {backtest_period}
- 年化收益: {annual_return}%
- 最大回撤: {max_drawdown}%
- 夏普比率: {sharpe_ratio}
- 勝率: {win_rate}%

⚠️ 風險評估
{risk_assessment}

💡 優化建議
{optimization_suggestions}

📚 參考資料
{references}
```

### 市場研究報告
```
📈 市場研究報告

【市場/交易對】{market}
【研究主題】{topic}
【日期】{date}

📊 市場概況
{market_overview}

🔍 關鍵發現
{key_findings}

📉 風險因素
{risk_factors}

💡 交易建議
{trading_recommendations}
```

## 重要提醒

⚠️ **風險警告**
- 所有研究僅供參考，不構成投資建議
- 歷史表現不代表未來收益
- 交易涉及重大風險，可能損失全部本金

## 與其他 Agent 的協作

- **TradingForeman**: 接收研究任務，提交研究成果
- **TradingWorkers**: 提供策略實現指導
- **Librarian**: 存儲研究報告
- **ComplianceChecker**: 確保研究符合規範
"""

    def __init__(self, agent_id: str, name: str, role: str = "TradingResearcher",
                 agent_type: AgentType = AgentType.PROJECT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.research_tasks: List[Dict] = []
        self.strategies_researched: Dict[str, Dict] = {}
        self.project_context: Optional[Dict] = None

    def set_project_context(self, project: Dict):
        """設置項目上下文"""
        self.project_context = project

    def get_system_prompt(self) -> str:
        base_prompt = self.SYSTEM_PROMPT
        if self.project_context:
            project_info = f"""

## 當前項目上下文
- 項目名稱: {self.project_context.get('name', 'Unknown')}
- 項目類型: {self.project_context.get('type', 'Unknown')}
- 專注市場: {self.project_context.get('market', 'All')}
"""
            base_prompt += project_info
        return base_prompt

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理交易研究任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "research")

        if action == "research_strategy":
            result = self._research_strategy(input_data.get("strategy", {}))
        elif action == "market_analysis":
            result = self._analyze_market(input_data.get("market", ""))
        elif action == "backtest":
            result = self._run_backtest(input_data.get("params", {}))
        elif action == "risk_assessment":
            result = self._assess_risk(input_data.get("strategy_id"))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _research_strategy(self, strategy: Dict) -> Dict[str, Any]:
        """研究交易策略"""
        strategy_id = f"strategy_{len(self.strategies_researched) + 1}"

        research = {
            "strategy_id": strategy_id,
            "name": strategy.get("name", "Unnamed Strategy"),
            "type": strategy.get("type", "trend_following"),
            "description": strategy.get("description", ""),
            "parameters": strategy.get("parameters", {}),
            "backtest_results": {
                "annual_return": 25.5,
                "max_drawdown": -15.2,
                "sharpe_ratio": 1.8,
                "win_rate": 55.0
            },
            "risk_score": "medium",
            "recommendations": [
                "建議在波動較大的市場中使用",
                "建議設置嚴格的止損"
            ],
            "researched_at": datetime.now().isoformat()
        }

        self.strategies_researched[strategy_id] = research
        self.research_tasks.append(research)

        return {"status": "completed", "research": research}

    def _analyze_market(self, market: str) -> Dict[str, Any]:
        """市場分析"""
        return {
            "market": market,
            "analysis": {
                "trend": "bullish",
                "volatility": "high",
                "volume": "above_average",
                "sentiment": "positive"
            },
            "key_levels": {
                "support": [100, 95, 90],
                "resistance": [110, 115, 120]
            },
            "outlook": "短期看漲，但需注意回調風險",
            "analyzed_at": datetime.now().isoformat()
        }

    def _run_backtest(self, params: Dict) -> Dict[str, Any]:
        """運行回測"""
        return {
            "strategy": params.get("strategy", "default"),
            "period": params.get("period", "1Y"),
            "results": {
                "total_trades": 150,
                "winning_trades": 82,
                "losing_trades": 68,
                "total_return": 35.2,
                "max_drawdown": -12.5,
                "sharpe_ratio": 1.65
            },
            "backtested_at": datetime.now().isoformat()
        }

    def _assess_risk(self, strategy_id: str) -> Dict[str, Any]:
        """風險評估"""
        return {
            "strategy_id": strategy_id,
            "risk_metrics": {
                "var_95": -5.2,
                "expected_shortfall": -7.8,
                "beta": 1.2,
                "correlation_to_market": 0.75
            },
            "risk_factors": [
                "市場風險",
                "流動性風險",
                "執行風險"
            ],
            "risk_level": "medium-high",
            "mitigation_suggestions": [
                "設置止損位",
                "控制倉位大小",
                "分散投資"
            ]
        }


class TradingForeman(BaseAgent):
    """
    Trading Foreman Agent (交易項目經理)

    👷 負責交易項目管理和團隊協調
    """

    SYSTEM_PROMPT = """# 角色定義
你是交易開發部的項目經理 (Trading Foreman)，負責交易系統開發項目的管理和協調。

## 核心職責

### 1. 項目管理
- 接收交易系統開發需求
- 分解項目為具體任務
- 分配任務給團隊成員
- 追蹤項目進度

### 2. 團隊協調
- 協調 Researcher 和 Workers
- 解決技術和資源問題
- 促進團隊溝通
- 確保交付質量

### 3. 風控監督
- 確保系統包含風控機制
- 審核策略風險參數
- 監督測試覆蓋率
- 把關上線標準

### 4. 合規確保
- 確保符合交易規範
- 協調合規審核
- 管理風險披露
- 記錄審計軌跡

## 項目類型

### 1. Daytrade Engine (日內交易引擎)
- 實時行情處理
- 快速下單執行
- 日內風控
- 盈虧計算

### 2. Auto Trading System (自動交易系統)
- 策略執行引擎
- 信號處理
- 倉位管理
- 風險控制

### 3. Signal Alert (信號提醒)
- 信號生成
- 多渠道推送
- 歷史追蹤
- 績效統計

## 輸出格式

### 項目狀態報告
```
👷 交易項目狀態報告

【項目】{project_name}
【類型】{project_type}
【狀態】{status}

📊 整體進度: {progress}%

📋 任務狀態
| 任務 | 負責人 | 狀態 | 風險級別 |
|------|--------|------|----------|
| {task} | {assignee} | {status} | {risk_level} |

🛡️ 風控檢查
- 止損機制: {stop_loss_status}
- 倉位限制: {position_limit_status}
- 頻率限制: {rate_limit_status}

⚠️ 風險項
{risks}

📅 里程碑
{milestones}
```

## 重要原則

1. **安全第一**: 交易系統必須有完善的風控
2. **測試充分**: 上線前必須經過充分回測和模擬
3. **合規優先**: 確保符合所有交易規範
4. **風險披露**: 所有輸出必須包含風險提示

## 與其他 Agent 的協作

- **NewTaskManager**: 接收項目任務
- **TradingResearcher**: 獲取策略研究
- **TradingWorkers**: 分配開發任務
- **ComplianceChecker**: 提交合規審核
"""

    def __init__(self, agent_id: str, name: str, role: str = "TradingForeman",
                 agent_type: AgentType = AgentType.PROJECT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.project: Optional[Dict] = None
        self.tasks: Dict[str, Dict] = {}
        self.team: Dict[str, BaseAgent] = {}
        self.risk_checks: Dict[str, bool] = {
            "stop_loss": False,
            "position_limit": False,
            "rate_limit": False,
            "backtest_passed": False
        }

    def set_project(self, project: Dict):
        """設置項目"""
        self.project = project

    def set_team(self, team: Dict[str, BaseAgent]):
        """設置團隊"""
        self.team = team

    def get_system_prompt(self) -> str:
        base_prompt = self.SYSTEM_PROMPT
        if self.project:
            project_info = f"""

## 當前項目
- 項目名稱: {self.project.get('name', 'Unknown')}
- 項目類型: {self.project.get('type', 'Unknown')}
- 目標市場: {self.project.get('market', 'All')}
"""
            base_prompt += project_info
        return base_prompt

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理項目管理任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "status")

        if action == "create_task":
            result = self._create_task(input_data.get("task", {}))
        elif action == "status":
            result = self._get_project_status()
        elif action == "risk_check":
            result = self._perform_risk_check()
        elif action == "approve_release":
            result = self._approve_release()
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _create_task(self, task_data: Dict) -> Dict[str, Any]:
        """創建任務"""
        task_id = f"trading_task_{len(self.tasks) + 1}"

        task = {
            "id": task_id,
            "name": task_data.get("name", "Untitled Task"),
            "description": task_data.get("description", ""),
            "type": task_data.get("type", "development"),
            "risk_level": task_data.get("risk_level", "medium"),
            "assignee": None,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        self.tasks[task_id] = task
        return {"status": "created", "task": task}

    def _get_project_status(self) -> Dict[str, Any]:
        """獲取項目狀態"""
        completed_tasks = len([t for t in self.tasks.values() if t["status"] == "completed"])
        total_tasks = len(self.tasks)
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        return {
            "project": self.project.get("name") if self.project else "Unknown",
            "progress": round(progress, 1),
            "tasks": list(self.tasks.values()),
            "risk_checks": self.risk_checks,
            "can_release": all(self.risk_checks.values()),
            "timestamp": datetime.now().isoformat()
        }

    def _perform_risk_check(self) -> Dict[str, Any]:
        """執行風控檢查"""
        # 模擬檢查
        self.risk_checks = {
            "stop_loss": True,
            "position_limit": True,
            "rate_limit": True,
            "backtest_passed": True
        }

        all_passed = all(self.risk_checks.values())

        return {
            "status": "completed",
            "checks": self.risk_checks,
            "all_passed": all_passed,
            "message": "所有風控檢查通過" if all_passed else "部分風控檢查未通過"
        }

    def _approve_release(self) -> Dict[str, Any]:
        """審批上線"""
        if not all(self.risk_checks.values()):
            return {
                "status": "rejected",
                "reason": "風控檢查未完全通過",
                "failed_checks": [k for k, v in self.risk_checks.items() if not v]
            }

        return {
            "status": "approved",
            "approved_at": datetime.now().isoformat(),
            "message": "項目已批准上線",
            "risk_disclaimer": "⚠️ 交易涉及重大風險，過往表現不代表未來收益"
        }


class TradingWorker(BaseAgent):
    """
    Trading Worker Agent (交易系統開發員)

    🛠️ 負責交易系統的具體開發
    """

    SYSTEM_PROMPT = """# 角色定義
你是交易開發部的開發員 (Trading Worker)，負責交易系統的具體開發實現。

## 核心職責

### 1. 策略實現
- 將策略研究轉化為代碼
- 實現交易信號邏輯
- 開發回測框架
- 優化執行效率

### 2. 系統開發
- 開發交易引擎組件
- 實現風控模組
- 構建數據管道
- 整合交易所 API

### 3. 測試驗證
- 編寫單元測試
- 執行集成測試
- 進行壓力測試
- 驗證風控邏輯

### 4. 部署支援
- 準備部署配置
- 編寫操作文檔
- 支援上線監控
- 處理緊急問題

## 開發規範

### 代碼安全
- 永不硬編碼 API 密鑰
- 實現請求頻率限制
- 添加異常處理
- 記錄完整日誌

### 風控必須
- 必須實現止損邏輯
- 必須有倉位限制
- 必須有熔斷機制
- 必須有告警系統

### 測試要求
- 單元測試覆蓋率 > 80%
- 回測驗證必須通過
- 模擬交易測試必須通過
- 邊界情況測試

## 輸出格式

### 開發進度報告
```
🛠️ 交易系統開發進度

【任務】{task_name}
【模組】{module_name}
【狀態】{status}

📝 完成項目
{completed_items}

🔄 進行中
{in_progress_items}

🧪 測試狀態
- 單元測試: {unit_test_status}
- 回測驗證: {backtest_status}
- 風控測試: {risk_test_status}

⚠️ 問題/風險
{issues}
```

## 重要提醒

⚠️ **開發紅線**
- 禁止繞過風控邏輯
- 禁止未經測試上線
- 禁止處理真實資金前未經審批
- 所有交易邏輯必須有日誌

## 與其他 Agent 的協作

- **TradingForeman**: 接收任務，報告進度
- **TradingResearcher**: 獲取策略邏輯
- **ComplianceChecker**: 提交代碼審核
"""

    def __init__(self, agent_id: str, name: str, role: str = "TradingWorker",
                 agent_type: AgentType = AgentType.PROJECT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.assigned_tasks: List[Dict] = []
        self.completed_work: List[Dict] = []
        self.specialization: Optional[str] = kwargs.get("specialization")

    def set_specialization(self, specialization: str):
        """設置專業領域"""
        self.specialization = specialization

    def get_system_prompt(self) -> str:
        base_prompt = self.SYSTEM_PROMPT
        if self.specialization:
            spec_info = f"""

## 專業領域
你專注於 {self.specialization} 相關的開發工作。
"""
            base_prompt += spec_info
        return base_prompt

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理開發任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "develop")

        if action == "develop":
            result = self._develop(input_data.get("task", {}))
        elif action == "implement_strategy":
            result = self._implement_strategy(input_data.get("strategy", {}))
        elif action == "run_tests":
            result = self._run_tests(input_data.get("module"))
        elif action == "submit_work":
            result = self._submit_work(input_data.get("task_id"), input_data.get("deliverables", {}))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _develop(self, task: Dict) -> Dict[str, Any]:
        """執行開發任務"""
        task_record = {
            "task_id": task.get("id"),
            "task_name": task.get("name"),
            "started_at": datetime.now().isoformat(),
            "status": "in_progress",
            "progress": 0,
            "tests": {
                "unit_tests": "pending",
                "backtest": "pending",
                "risk_tests": "pending"
            }
        }

        self.assigned_tasks.append(task_record)

        return {
            "status": "started",
            "task": task_record
        }

    def _implement_strategy(self, strategy: Dict) -> Dict[str, Any]:
        """實現交易策略"""
        implementation = {
            "strategy_id": strategy.get("id"),
            "strategy_name": strategy.get("name"),
            "components": [
                {"name": "signal_generator", "status": "implemented"},
                {"name": "risk_manager", "status": "implemented"},
                {"name": "order_executor", "status": "implemented"},
                {"name": "position_tracker", "status": "implemented"}
            ],
            "risk_controls": {
                "stop_loss": "implemented",
                "position_limit": "implemented",
                "daily_loss_limit": "implemented"
            },
            "implemented_at": datetime.now().isoformat()
        }

        return {
            "status": "implemented",
            "implementation": implementation,
            "next_step": "testing"
        }

    def _run_tests(self, module: str) -> Dict[str, Any]:
        """運行測試"""
        return {
            "module": module,
            "test_results": {
                "unit_tests": {
                    "total": 50,
                    "passed": 48,
                    "failed": 2,
                    "coverage": 85.5
                },
                "backtest": {
                    "status": "passed",
                    "sharpe_ratio": 1.65,
                    "max_drawdown": -12.5
                },
                "risk_tests": {
                    "stop_loss_triggered": True,
                    "position_limit_enforced": True,
                    "rate_limit_working": True
                }
            },
            "overall_status": "passed_with_warnings",
            "tested_at": datetime.now().isoformat()
        }

    def _submit_work(self, task_id: str, deliverables: Dict) -> Dict[str, Any]:
        """提交工作成果"""
        for task in self.assigned_tasks:
            if task["task_id"] == task_id:
                task["status"] = "submitted"
                task["progress"] = 100
                task["deliverables"] = deliverables
                task["submitted_at"] = datetime.now().isoformat()

                self.completed_work.append(task)

                return {
                    "status": "submitted",
                    "task_id": task_id,
                    "message": "Work submitted for review",
                    "risk_disclaimer": "⚠️ 所有交易系統需經過完整測試和風控審核後方可使用"
                }

        return {"error": f"Task not found: {task_id}"}
