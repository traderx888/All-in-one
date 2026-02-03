"""
============================================================
Product Dev Team Templates
產品開發部動態團隊模板
============================================================

標準團隊結構: Researcher → Foreman → Workers

這些模板用於動態生成項目團隊
每當有新項目時，系統會基於這些模板實例化專屬團隊
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

import sys
sys.path.append('../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class Researcher(BaseAgent):
    """
    Researcher Agent (研究員)

    🔍 負責項目的研究和調研工作
    """

    SYSTEM_PROMPT = """# 角色定義
你是產品開發部的研究員 (Researcher)，專注於項目研究和調研。

## 核心職責

### 1. 需求研究
- 分析項目需求背景
- 研究用戶痛點
- 調查市場現狀
- 評估競品方案

### 2. 技術調研
- 研究可行的技術方案
- 評估技術風險
- 調研最佳實踐
- 收集技術參考

### 3. 資料整理
- 整理研究發現
- 撰寫調研報告
- 提供決策建議
- 建立知識庫

### 4. 持續支援
- 解答開發中的問題
- 補充額外調研
- 追蹤行業動態
- 更新研究結論

## 研究框架

### 市場研究
1. 目標市場定義
2. 用戶需求分析
3. 競品分析
4. 市場趨勢

### 技術研究
1. 技術可行性
2. 架構選型
3. 工具評估
4. 風險識別

## 輸出格式

### 調研報告
```
🔍 調研報告

【項目】{project_name}
【研究主題】{topic}
【研究日期】{date}

📊 研究摘要
{executive_summary}

📋 詳細發現
## 1. {finding_category_1}
{detailed_findings_1}

## 2. {finding_category_2}
{detailed_findings_2}

📈 數據支持
{supporting_data}

⚠️ 風險與挑戰
{risks_and_challenges}

💡 建議
{recommendations}

📚 參考資料
{references}
```

## 與其他 Agent 的協作

- **Foreman**: 接收研究任務，提交研究成果
- **Workers**: 提供技術指導和參考
- **Librarian**: 存儲和查詢研究資料
- **MasterArchitect**: 獲取架構指導
"""

    def __init__(self, agent_id: str, name: str, role: str = "Researcher",
                 agent_type: AgentType = AgentType.PROJECT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.research_tasks: List[Dict] = []
        self.findings: Dict[str, Dict] = {}
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
- 項目描述: {self.project_context.get('description', 'No description')}
"""
            base_prompt += project_info
        return base_prompt

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理研究任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "research")

        if action == "research":
            result = self._conduct_research(input_data.get("topic", ""))
        elif action == "analyze_competitors":
            result = self._analyze_competitors(input_data.get("competitors", []))
        elif action == "tech_evaluation":
            result = self._evaluate_technology(input_data.get("technologies", []))
        elif action == "get_findings":
            result = self._get_findings(input_data.get("task_id"))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _conduct_research(self, topic: str) -> Dict[str, Any]:
        """進行研究"""
        task_id = f"research_{len(self.research_tasks) + 1}"

        research_result = {
            "task_id": task_id,
            "topic": topic,
            "project": self.project_context.get("name") if self.project_context else "Unknown",
            "summary": f"針對 {topic} 的研究摘要",
            "findings": [
                {"category": "市場", "finding": "市場需求分析結果"},
                {"category": "技術", "finding": "技術可行性分析結果"},
                {"category": "競品", "finding": "競品分析結果"}
            ],
            "recommendations": [
                "基於研究的建議1",
                "基於研究的建議2"
            ],
            "risks": [
                "識別的風險1",
                "識別的風險2"
            ],
            "researched_at": datetime.now().isoformat()
        }

        self.research_tasks.append(research_result)
        self.findings[task_id] = research_result

        return {"status": "completed", "research": research_result}

    def _analyze_competitors(self, competitors: List[str]) -> Dict[str, Any]:
        """競品分析"""
        analysis = []
        for comp in competitors:
            analysis.append({
                "name": comp,
                "strengths": ["優勢1", "優勢2"],
                "weaknesses": ["劣勢1", "劣勢2"],
                "features": ["功能1", "功能2"],
                "pricing": "競品定價信息"
            })

        return {
            "status": "completed",
            "competitor_analysis": analysis,
            "summary": f"分析了 {len(competitors)} 個競品"
        }

    def _evaluate_technology(self, technologies: List[str]) -> Dict[str, Any]:
        """技術評估"""
        evaluations = []
        for tech in technologies:
            evaluations.append({
                "technology": tech,
                "suitability": "高",
                "complexity": "中",
                "community_support": "活躍",
                "recommendation": "推薦使用"
            })

        return {
            "status": "completed",
            "tech_evaluation": evaluations
        }

    def _get_findings(self, task_id: str) -> Dict[str, Any]:
        """獲取研究發現"""
        if task_id in self.findings:
            return {"status": "found", "findings": self.findings[task_id]}
        return {"status": "not_found", "message": f"No findings for task: {task_id}"}


class Foreman(BaseAgent):
    """
    Foreman Agent (工頭)

    👷 負責項目管理和團隊協調
    """

    SYSTEM_PROMPT = """# 角色定義
你是產品開發部的工頭 (Foreman)，負責項目管理和團隊協調。

## 核心職責

### 1. 需求對接
- 接收上級的項目需求
- 理解並分解需求
- 確認需求細節
- 管理需求變更

### 2. 任務分配
- 將項目分解為具體任務
- 分配任務給 Researcher 和 Workers
- 設定任務優先級
- 規劃時間線

### 3. 進度監督
- 追蹤各任務進度
- 識別和處理阻礙
- 協調團隊資源
- 更新項目狀態

### 4. 質量把控
- 審核交付成果
- 確保符合需求
- 協調問題修復
- 驗收最終產出

## 項目管理框架

### 階段劃分
1. **啟動階段**: 需求確認、團隊組建
2. **研究階段**: Researcher 進行調研
3. **開發階段**: Workers 進行開發
4. **測試階段**: 功能測試和修復
5. **交付階段**: 驗收和上線

### 任務狀態
- `pending`: 待開始
- `in_progress`: 進行中
- `blocked`: 被阻塞
- `review`: 待審核
- `completed`: 已完成

## 輸出格式

### 項目狀態報告
```
👷 項目狀態報告

【項目】{project_name}
【狀態】{status}
【報告時間】{timestamp}

📊 整體進度: {progress}%

📋 任務概覽
| 任務 | 負責人 | 狀態 | 進度 |
|------|--------|------|------|
| {task} | {assignee} | {status} | {progress}% |

⚠️ 阻礙項
{blockers}

📅 下一步
{next_steps}

📝 備註
{notes}
```

### 任務分配通知
```
📌 任務分配

【任務】{task_name}
【分配給】{assignee}
【優先級】{priority}
【截止時間】{deadline}

📝 任務描述
{description}

✅ 驗收標準
{acceptance_criteria}

📎 相關資源
{resources}
```

## 與其他 Agent 的協作

- **NewTaskManager**: 接收項目任務
- **Researcher**: 分配研究任務，接收研究成果
- **Workers**: 分配開發任務，監督進度
- **ComplianceChecker**: 提交代碼審核
- **MasterArchitect**: 獲取架構指導
"""

    def __init__(self, agent_id: str, name: str, role: str = "Foreman",
                 agent_type: AgentType = AgentType.PROJECT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.project: Optional[Dict] = None
        self.tasks: Dict[str, Dict] = {}
        self.team: Dict[str, BaseAgent] = {}

    def set_project(self, project: Dict):
        """設置項目"""
        self.project = project

    def set_team(self, team: Dict[str, BaseAgent]):
        """設置團隊成員"""
        self.team = team

    def get_system_prompt(self) -> str:
        base_prompt = self.SYSTEM_PROMPT
        if self.project:
            project_info = f"""

## 當前項目
- 項目名稱: {self.project.get('name', 'Unknown')}
- 項目描述: {self.project.get('description', 'No description')}
- 團隊規模: {len(self.team)} 人
"""
            base_prompt += project_info
        return base_prompt

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理項目管理任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "status")

        if action == "create_task":
            result = self._create_task(input_data.get("task", {}))
        elif action == "assign_task":
            result = self._assign_task(
                input_data.get("task_id"),
                input_data.get("assignee")
            )
        elif action == "update_task":
            result = self._update_task_status(
                input_data.get("task_id"),
                input_data.get("status")
            )
        elif action == "status":
            result = self._get_project_status()
        elif action == "decompose":
            result = self._decompose_requirements(input_data.get("requirements", {}))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _create_task(self, task_data: Dict) -> Dict[str, Any]:
        """創建任務"""
        task_id = f"task_{len(self.tasks) + 1}"

        task = {
            "id": task_id,
            "name": task_data.get("name", "Untitled Task"),
            "description": task_data.get("description", ""),
            "type": task_data.get("type", "development"),  # research, development, testing
            "priority": task_data.get("priority", "medium"),
            "assignee": None,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "deadline": task_data.get("deadline"),
            "acceptance_criteria": task_data.get("acceptance_criteria", [])
        }

        self.tasks[task_id] = task
        return {"status": "created", "task": task}

    def _assign_task(self, task_id: str, assignee: str) -> Dict[str, Any]:
        """分配任務"""
        if task_id not in self.tasks:
            return {"error": f"Task not found: {task_id}"}

        self.tasks[task_id]["assignee"] = assignee
        self.tasks[task_id]["status"] = "assigned"

        return {
            "status": "assigned",
            "task_id": task_id,
            "assignee": assignee
        }

    def _update_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        """更新任務狀態"""
        if task_id not in self.tasks:
            return {"error": f"Task not found: {task_id}"}

        self.tasks[task_id]["status"] = status

        # 根據狀態更新進度
        progress_map = {
            "pending": 0,
            "assigned": 10,
            "in_progress": 50,
            "review": 80,
            "completed": 100
        }
        self.tasks[task_id]["progress"] = progress_map.get(status, 0)

        return {
            "status": "updated",
            "task_id": task_id,
            "new_status": status
        }

    def _get_project_status(self) -> Dict[str, Any]:
        """獲取項目狀態"""
        if not self.tasks:
            overall_progress = 0
        else:
            overall_progress = sum(t["progress"] for t in self.tasks.values()) / len(self.tasks)

        return {
            "project": self.project.get("name") if self.project else "Unknown",
            "overall_progress": round(overall_progress, 1),
            "tasks": list(self.tasks.values()),
            "team_size": len(self.team),
            "blockers": [],
            "timestamp": datetime.now().isoformat()
        }

    def _decompose_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """分解需求為任務"""
        tasks_created = []

        # 研究任務
        research_task = self._create_task({
            "name": f"Research: {requirements.get('title', 'Project')}",
            "description": "進行項目相關的研究和調研",
            "type": "research",
            "priority": "high"
        })
        tasks_created.append(research_task["task"])

        # 開發任務 (根據模組數量)
        modules = requirements.get("modules", ["core"])
        for module in modules:
            dev_task = self._create_task({
                "name": f"Develop: {module}",
                "description": f"開發 {module} 模組",
                "type": "development",
                "priority": "medium"
            })
            tasks_created.append(dev_task["task"])

        # 測試任務
        test_task = self._create_task({
            "name": "Testing and QA",
            "description": "功能測試和質量保證",
            "type": "testing",
            "priority": "high"
        })
        tasks_created.append(test_task["task"])

        return {
            "status": "decomposed",
            "tasks_created": len(tasks_created),
            "tasks": tasks_created
        }


class Worker(BaseAgent):
    """
    Worker Agent (開發員)

    🛠️ 負責具體的開發工作
    """

    SYSTEM_PROMPT = """# 角色定義
你是產品開發部的開發員 (Worker)，負責具體的開發實現工作。

## 核心職責

### 1. 代碼開發
- 根據任務需求編寫代碼
- 遵循代碼規範
- 實現功能模組
- 處理邊界情況

### 2. 技術實現
- 選擇適當的技術方案
- 處理技術難點
- 優化性能
- 確保代碼質量

### 3. 測試與調試
- 編寫單元測試
- 進行功能調試
- 修復 Bug
- 確保代碼穩定

### 4. 文檔與交付
- 編寫技術文檔
- 提交代碼審核
- 配合 Foreman 驗收
- 支援部署上線

## 開發規範

### 代碼風格
- 遵循語言標準風格指南
- 有意義的變量和函數命名
- 適當的註釋
- 模組化設計

### 提交規範
- 清晰的 commit message
- 小步提交
- 功能完整後再合併
- 關聯任務 ID

### 安全規範
- 不硬編碼敏感信息
- 輸入驗證
- 錯誤處理
- 日誌記錄

## 輸出格式

### 開發進度報告
```
🛠️ 開發進度報告

【任務】{task_name}
【狀態】{status}
【進度】{progress}%

📝 完成項目
{completed_items}

🔄 進行中
{in_progress_items}

⚠️ 問題/阻礙
{issues}

📅 預計完成
{estimated_completion}
```

### 代碼交付
```
✅ 代碼交付

【任務】{task_name}
【模組】{module_name}

📁 文件變更
{file_changes}

🧪 測試覆蓋
{test_coverage}

📋 交付清單
- [ ] 功能實現
- [ ] 單元測試
- [ ] 文檔更新
- [ ] 代碼審核

📝 備註
{notes}
```

## 與其他 Agent 的協作

- **Foreman**: 接收任務，報告進度
- **Researcher**: 獲取研究成果和技術指導
- **ComplianceChecker**: 提交代碼安全審核
- **其他 Workers**: 協作完成複雜功能
"""

    def __init__(self, agent_id: str, name: str, role: str = "Worker",
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
        elif action == "report_progress":
            result = self._report_progress(input_data.get("task_id"))
        elif action == "submit_work":
            result = self._submit_work(input_data.get("task_id"), input_data.get("deliverables", {}))
        elif action == "fix_bug":
            result = self._fix_bug(input_data.get("bug", {}))
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
            "work_items": []
        }

        self.assigned_tasks.append(task_record)

        return {
            "status": "started",
            "task": task_record,
            "message": f"Started working on: {task.get('name')}"
        }

    def _report_progress(self, task_id: str) -> Dict[str, Any]:
        """報告進度"""
        for task in self.assigned_tasks:
            if task["task_id"] == task_id:
                return {
                    "task_id": task_id,
                    "status": task["status"],
                    "progress": task["progress"],
                    "work_items": task["work_items"],
                    "started_at": task["started_at"]
                }

        return {"error": f"Task not found: {task_id}"}

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
                    "deliverables": deliverables,
                    "message": "Work submitted for review"
                }

        return {"error": f"Task not found: {task_id}"}

    def _fix_bug(self, bug: Dict) -> Dict[str, Any]:
        """修復 Bug"""
        fix_record = {
            "bug_id": bug.get("id"),
            "description": bug.get("description"),
            "fix_description": f"Fixed: {bug.get('description')}",
            "fixed_at": datetime.now().isoformat()
        }

        return {
            "status": "fixed",
            "fix": fix_record
        }
