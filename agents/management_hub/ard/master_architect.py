"""
============================================================
Master Architect Agent
首席架構師 - 系統設計的最高權威
============================================================

角色定位:
- 負責所有架構設計決策
- 解構複雜需求為可執行模組
- 設計新 Agent 的架構和 Prompt
- 審核技術方案

工作流程:
1. 接收開發模式任務
2. 分析需求，進行架構解構
3. 設計系統架構和組件
4. 定義接口和通訊協議
5. 創建實現規範
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

import sys
sys.path.append('../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class DesignPhase(Enum):
    """設計階段"""
    ANALYSIS = "analysis"
    ARCHITECTURE = "architecture"
    DETAILED_DESIGN = "detailed_design"
    SPECIFICATION = "specification"
    REVIEW = "review"


@dataclass
class ArchitectureDesign:
    """架構設計文檔"""
    id: str
    name: str
    phase: DesignPhase
    components: List[Dict]
    interfaces: List[Dict]
    data_flows: List[Dict]
    constraints: List[str]
    created_at: datetime
    status: str = "draft"


class MasterArchitect(BaseAgent):
    """
    首席架構師 Agent

    🏛️ 負責系統架構設計，是技術決策的最高權威
    """

    SYSTEM_PROMPT = """# 角色定義
你是 AI 組織的首席架構師 (MasterArchitect)，Zone ARD 的技術設計權威。

## 核心職責

### 1. 需求解構
- 分析業務需求背後的技術需求
- 識別功能性和非功能性需求
- 評估技術可行性
- 識別風險和約束

### 2. 架構設計
- 設計系統整體架構
- 定義組件和模組
- 規劃數據流和控制流
- 選擇適當的設計模式

### 3. Agent 設計
- 設計新 Agent 的角色定位
- 撰寫 Agent 的 System Prompt
- 定義 Agent 的輸入輸出接口
- 規劃 Agent 間的協作關係

### 4. 技術審核
- 審核技術方案
- 評估架構決策
- 識別潛在問題
- 提供改進建議

## 架構設計原則

### 1. 單一職責 (Single Responsibility)
- 每個 Agent 只負責一個明確的領域
- 避免 Agent 職責過重
- 清晰的邊界定義

### 2. 鬆散耦合 (Loose Coupling)
- Agent 間通過標準接口通訊
- 避免直接依賴
- 使用消息總線

### 3. 高內聚 (High Cohesion)
- 相關功能集中在同一 Agent
- 減少跨 Agent 調用
- 數據本地化

### 4. 可擴展性 (Scalability)
- 支持動態添加 Agent
- 水平擴展能力
- 資源彈性配置

### 5. 可觀測性 (Observability)
- 所有操作可追蹤
- 狀態可查詢
- 性能可監控

## Agent 設計模板

當設計新 Agent 時，遵循以下結構:

```
# Agent 設計規範

## 1. 基本信息
- 名稱: {AgentName}
- 角色: {role description}
- 類型: PERMANENT / PROJECT / CHAIN
- 所屬: {department/zone}

## 2. 職責範圍
- 主要職責:
  1. {responsibility_1}
  2. {responsibility_2}
- 不應處理:
  1. {out_of_scope_1}

## 3. 輸入輸出
- 輸入:
  ```json
  {
    "action": "string",
    "params": {}
  }
  ```
- 輸出:
  ```json
  {
    "status": "string",
    "result": {}
  }
  ```

## 4. 協作關係
- 上游: {upstream_agents}
- 下游: {downstream_agents}
- 平行: {peer_agents}

## 5. System Prompt 大綱
- 角色定義
- 核心職責
- 工作流程
- 輸出格式
- 工作原則
```

## 輸出格式

### 架構設計報告
```
🏛️ 架構設計報告

【項目】{project_name}
【版本】{version}
【狀態】{DRAFT/IN_REVIEW/APPROVED}

📋 需求分析
- 業務目標: {goal}
- 技術需求: {requirements}
- 約束條件: {constraints}

🧱 架構概覽
{架構圖的文字描述}

📦 組件設計
| 組件 | 類型 | 職責 | 依賴 |
|------|------|------|------|
| {name} | {type} | {responsibility} | {deps} |

🔗 接口定義
{接口規範}

📊 數據流
{數據流描述}

⚠️ 風險評估
{風險列表及緩解措施}

📝 下一步
{後續行動項}
```

### Agent Prompt 設計
```
📝 Agent Prompt 設計

【Agent 名稱】{name}
【設計版本】{version}

---

{完整的 System Prompt 內容}

---

【設計說明】
- 設計理念: {rationale}
- 關鍵考量: {considerations}
- 預期行為: {expected_behavior}
```

## 架構模式庫

### 1. 流水線模式 (Pipeline)
適用於: Content Dev 的內容生產鏈
結構: Input → Stage1 → Stage2 → ... → Output

### 2. 團隊模式 (Team)
適用於: Product Dev, Trading Dev 的項目開發
結構: Researcher → Foreman → Workers

### 3. 監控模式 (Observer)
適用於: 系統監控、合規檢查
結構: Observer ← Subject (定期報告)

### 4. 路由模式 (Router)
適用於: Secretary 的意圖路由
結構: Input → Router → [Handler1, Handler2, ...]

## 工作原則

1. **簡單優先**: 選擇最簡單可行的方案
2. **迭代設計**: 允許架構隨需求演進
3. **文檔先行**: 設計文檔必須在實現之前完成
4. **審核必須**: 重大架構決策需要審核
5. **經驗復用**: 積累和復用成功的設計模式

## 與其他 Agent 的協作

- **NewTaskManager**: 接收開發任務，報告設計進度
- **ComplianceChecker**: 確保架構符合合規要求
- **Librarian**: 存儲和檢索架構文檔
- **各部門 Foreman**: 提供技術指導
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.PERMANENT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.designs: Dict[str, ArchitectureDesign] = {}
        self.design_history: List[Dict] = []
        self.patterns_library: Dict[str, Dict] = self._init_patterns()

    def _init_patterns(self) -> Dict[str, Dict]:
        """初始化設計模式庫"""
        return {
            "pipeline": {
                "name": "Pipeline Pattern",
                "description": "Sequential processing stages",
                "use_cases": ["content_generation", "data_processing"],
                "template": {
                    "stages": ["input", "process", "output"],
                    "connectors": "sequential"
                }
            },
            "team": {
                "name": "Team Pattern",
                "description": "Researcher-Foreman-Workers structure",
                "use_cases": ["project_development", "research_tasks"],
                "template": {
                    "roles": ["researcher", "foreman", "workers"],
                    "hierarchy": "foreman_leads"
                }
            },
            "observer": {
                "name": "Observer Pattern",
                "description": "Monitoring and reporting",
                "use_cases": ["system_monitoring", "compliance_checking"],
                "template": {
                    "observer": "monitors",
                    "subject": "reports_status"
                }
            },
            "router": {
                "name": "Router Pattern",
                "description": "Intent-based routing",
                "use_cases": ["request_handling", "task_distribution"],
                "template": {
                    "router": "analyzes_and_routes",
                    "handlers": "process_specific_types"
                }
            }
        }

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理架構設計請求

        Args:
            input_data: {
                "action": str,          # analyze, design, design_agent, review
                "requirements": dict,   # 需求描述
                "design_id": str        # 設計 ID (for review)
            }

        Returns:
            設計結果
        """
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "analyze")

        if action == "analyze":
            result = self._analyze_requirements(input_data.get("requirements", {}))
        elif action == "design":
            result = self._create_architecture_design(input_data.get("requirements", {}))
        elif action == "design_agent":
            result = self._design_agent(input_data.get("requirements", {}))
        elif action == "review":
            result = self._review_design(input_data.get("design_id", ""))
        elif action == "get_pattern":
            result = self._get_pattern(input_data.get("pattern_name", ""))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _analyze_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """分析需求"""
        title = requirements.get("title", "")
        description = requirements.get("description", "")

        # 識別適用的設計模式
        applicable_patterns = []
        if "content" in description.lower() or "pipeline" in description.lower():
            applicable_patterns.append("pipeline")
        if "project" in description.lower() or "develop" in description.lower():
            applicable_patterns.append("team")
        if "monitor" in description.lower() or "check" in description.lower():
            applicable_patterns.append("observer")
        if "route" in description.lower() or "dispatch" in description.lower():
            applicable_patterns.append("router")

        # 評估複雜度
        complexity = "medium"
        if "simple" in description.lower():
            complexity = "low"
        elif "complex" in description.lower() or "multiple" in description.lower():
            complexity = "high"

        return {
            "analysis": {
                "title": title,
                "complexity": complexity,
                "applicable_patterns": applicable_patterns,
                "estimated_components": len(applicable_patterns) + 2,
                "risks": ["需要進一步細化需求", "可能需要跨部門協作"]
            },
            "recommendation": {
                "primary_pattern": applicable_patterns[0] if applicable_patterns else "custom",
                "approach": "iterative_design"
            }
        }

    def _create_architecture_design(self, requirements: Dict) -> Dict[str, Any]:
        """創建架構設計"""
        import uuid

        design_id = f"design_{uuid.uuid4().hex[:8]}"

        # 基於需求生成組件
        components = [
            {
                "name": "InputHandler",
                "type": "interface",
                "responsibility": "接收和驗證輸入"
            },
            {
                "name": "CoreProcessor",
                "type": "processor",
                "responsibility": "核心業務邏輯處理"
            },
            {
                "name": "OutputFormatter",
                "type": "formatter",
                "responsibility": "格式化輸出結果"
            }
        ]

        design = ArchitectureDesign(
            id=design_id,
            name=requirements.get("title", "Unnamed Design"),
            phase=DesignPhase.ARCHITECTURE,
            components=components,
            interfaces=[
                {"name": "process", "input": "Dict", "output": "Dict"}
            ],
            data_flows=[
                {"from": "InputHandler", "to": "CoreProcessor"},
                {"from": "CoreProcessor", "to": "OutputFormatter"}
            ],
            constraints=requirements.get("constraints", []),
            created_at=datetime.now()
        )

        self.designs[design_id] = design

        return {
            "design_id": design_id,
            "name": design.name,
            "phase": design.phase.value,
            "components": components,
            "status": "created"
        }

    def _design_agent(self, requirements: Dict) -> Dict[str, Any]:
        """設計新 Agent"""
        agent_name = requirements.get("name", "NewAgent")
        role = requirements.get("role", "")
        responsibilities = requirements.get("responsibilities", [])

        # 生成 System Prompt 框架
        prompt_template = f"""# 角色定義
你是 AI 組織的 {agent_name}，負責 {role}。

## 核心職責

{chr(10).join(f'### {i+1}. {r}' for i, r in enumerate(responsibilities))}

## 工作流程

1. 接收任務輸入
2. 分析任務需求
3. 執行核心邏輯
4. 生成輸出結果
5. 報告執行狀態

## 輸出格式

### 任務完成報告
```
✅ 任務完成報告

【任務】{{task_name}}
【狀態】{{status}}
【結果】
{{result_details}}
```

## 工作原則

1. 準確執行分配的任務
2. 及時報告進度和問題
3. 遵守組織的合規要求
4. 與相關 Agent 保持協作

## 與其他 Agent 的協作

- 上游: {{upstream_agents}}
- 下游: {{downstream_agents}}
"""

        return {
            "agent_design": {
                "name": agent_name,
                "role": role,
                "type": requirements.get("type", "PROJECT"),
                "department": requirements.get("department", "general"),
                "responsibilities": responsibilities
            },
            "system_prompt": prompt_template,
            "interface": {
                "input": {
                    "action": "string",
                    "params": "Dict[str, Any]"
                },
                "output": {
                    "status": "string",
                    "result": "Dict[str, Any]"
                }
            }
        }

    def _review_design(self, design_id: str) -> Dict[str, Any]:
        """審核設計"""
        if design_id not in self.designs:
            return {"error": f"Design not found: {design_id}"}

        design = self.designs[design_id]

        # 執行審核檢查
        checks = {
            "has_components": len(design.components) > 0,
            "has_interfaces": len(design.interfaces) > 0,
            "has_data_flows": len(design.data_flows) > 0,
            "components_connected": True  # 簡化檢查
        }

        passed = all(checks.values())
        design.status = "approved" if passed else "needs_revision"
        design.phase = DesignPhase.REVIEW

        return {
            "design_id": design_id,
            "review_result": "APPROVED" if passed else "NEEDS_REVISION",
            "checks": checks,
            "comments": [] if passed else ["請確保所有組件都有明確的接口定義"]
        }

    def _get_pattern(self, pattern_name: str) -> Dict[str, Any]:
        """獲取設計模式"""
        if pattern_name in self.patterns_library:
            return {
                "pattern": self.patterns_library[pattern_name]
            }
        return {
            "available_patterns": list(self.patterns_library.keys())
        }
