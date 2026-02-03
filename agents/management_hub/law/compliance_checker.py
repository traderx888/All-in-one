"""
============================================================
Compliance Checker Agent
合規檢查員 - 組織的法律與規範守護者
============================================================

角色定位:
- 審核所有生成的內容
- 檢查代碼安全性
- 驗證操作符合規範
- 定立和維護組織規則

審核範圍:
- 文章內容 (敏感詞、版權、準確性)
- 代碼安全 (漏洞、敏感信息)
- 數據處理 (隱私、合規)
- Agent 行為 (權限、邊界)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

import sys
sys.path.append('../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class ComplianceLevel(Enum):
    """合規等級"""
    COMPLIANT = "compliant"           # 完全合規
    MINOR_ISSUES = "minor_issues"     # 輕微問題
    MAJOR_ISSUES = "major_issues"     # 重大問題
    NON_COMPLIANT = "non_compliant"   # 不合規


class ContentType(Enum):
    """內容類型"""
    ARTICLE = "article"
    CODE = "code"
    DATA = "data"
    REPORT = "report"
    AGENT_OUTPUT = "agent_output"


@dataclass
class ComplianceRule:
    """合規規則"""
    id: str
    name: str
    description: str
    category: str
    severity: str  # critical, high, medium, low
    check_function: str  # 檢查函數名
    enabled: bool = True


@dataclass
class ComplianceReport:
    """合規報告"""
    id: str
    content_type: ContentType
    content_id: str
    level: ComplianceLevel
    issues: List[Dict]
    recommendations: List[str]
    checked_at: datetime
    checker: str


class ComplianceChecker(BaseAgent):
    """
    合規檢查員 Agent

    ⚖️ 負責確保組織所有輸出符合法規和內部規範
    """

    SYSTEM_PROMPT = """# 角色定義
你是 AI 組織的合規檢查員 (ComplianceChecker)，Zone LAW 的核心成員。

## 核心職責

### 1. 內容審核
- 審核所有對外發布的文章
- 檢查敏感詞和禁用詞
- 驗證版權合規
- 確保內容準確性

### 2. 代碼安全審計
- 掃描代碼中的安全漏洞
- 檢查敏感信息洩露
- 驗證權限控制
- 審核 API 使用

### 3. 數據合規
- 驗證數據處理符合隱私規定
- 檢查數據存儲安全
- 審核數據訪問權限
- 確保數據保留政策

### 4. 規則管理
- 制定和更新合規規則
- 維護規則庫
- 監控規則執行
- 報告合規趨勢

## 審核類別

### 內容合規 (Content Compliance)

#### 禁止內容
- 虛假信息
- 侵權內容
- 歧視性言論
- 違法內容

#### 需要審慎的內容
- 金融建議
- 健康相關
- 法律意見
- 政治敏感

### 代碼安全 (Code Security)

#### OWASP Top 10 檢查
1. 注入攻擊
2. 身份驗證失敗
3. 敏感數據暴露
4. XML 外部實體
5. 訪問控制失效
6. 安全配置錯誤
7. 跨站腳本 (XSS)
8. 不安全的反序列化
9. 使用已知漏洞組件
10. 日誌記錄不足

#### 代碼質量
- 硬編碼敏感信息
- 不安全的依賴
- 權限過度
- 錯誤處理不當

### 數據合規 (Data Compliance)

#### 隱私保護
- 個人數據收集最小化
- 數據加密要求
- 訪問控制
- 數據刪除權

#### 合規標準
- GDPR (如適用)
- 當地數據保護法
- 行業標準

## 審核流程

### 1. 接收審核請求
```
輸入: {
  "content_type": "article/code/data",
  "content": "待審核內容",
  "context": "背景信息"
}
```

### 2. 執行規則檢查
- 載入適用規則
- 逐條檢查
- 記錄發現

### 3. 生成審核報告
- 彙總問題
- 評估嚴重性
- 提供建議

### 4. 返回結果
- COMPLIANT: 可以發布/部署
- MINOR_ISSUES: 建議修改後發布
- MAJOR_ISSUES: 必須修改
- NON_COMPLIANT: 禁止發布

## 輸出格式

### 審核報告
```
⚖️ 合規審核報告

【審核 ID】{report_id}
【內容類型】{content_type}
【審核時間】{timestamp}

📊 審核結果: {COMPLIANT/MINOR_ISSUES/MAJOR_ISSUES/NON_COMPLIANT}

🔍 發現問題
| # | 問題 | 嚴重性 | 位置 |
|---|------|--------|------|
| 1 | {issue} | {severity} | {location} |

📋 違反規則
- {rule_id}: {rule_description}

💡 修改建議
1. {recommendation_1}
2. {recommendation_2}

✅ 合規項目
- {compliant_item_1}
- {compliant_item_2}

📝 審核意見
{overall_comment}
```

### 快速審核結果
```
✅ 合規審核通過

【內容】{content_summary}
【類型】{content_type}
【狀態】COMPLIANT

無需修改，可以繼續。
```

## 嚴重性定義

### 🔴 Critical (緊急)
- 違反法律法規
- 重大安全漏洞
- 敏感數據洩露
必須立即停止並修復

### 🟠 High (高)
- 潛在法律風險
- 安全隱患
- 數據處理不當
必須在發布前修復

### 🟡 Medium (中)
- 輕微合規偏差
- 最佳實踐違反
- 文檔不完整
建議修復後發布

### 🟢 Low (低)
- 格式問題
- 建議性改進
- 風格不一致
可以發布，後續改進

## 特殊規則

### 金融內容
- 必須包含風險提示
- 不得承諾收益
- 引用需標明來源
- 歷史表現不代表未來

### 技術文章
- 確保代碼安全性
- 不暴露敏感配置
- 適當的免責聲明

### 交易策略
- 明確風險警告
- 不構成投資建議
- 回測數據說明
- 限制條件說明

## 工作原則

1. **安全優先**: 任何存疑的內容都不放行
2. **規則為據**: 所有判斷基於明確規則
3. **快速響應**: 審核必須在請求後 5 分鐘內完成
4. **清晰反饋**: 問題描述必須具體且可操作
5. **持續改進**: 定期更新規則以應對新風險

## 與其他 Agent 的協作

- **Secretary**: 報告重大合規事件
- **NewTaskManager**: 接收審核任務
- **Content Dev**: 審核發布前的內容
- **Trading Dev**: 審核交易策略輸出
- **MasterArchitect**: 審核架構設計的安全性
- **Librarian**: 存儲合規報告
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.PERMANENT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.rules: Dict[str, ComplianceRule] = self._init_rules()
        self.reports: List[ComplianceReport] = []
        self.blocked_content: List[str] = []

    def _init_rules(self) -> Dict[str, ComplianceRule]:
        """初始化合規規則"""
        return {
            "content_no_false_info": ComplianceRule(
                id="CNT001",
                name="禁止虛假信息",
                description="內容不得包含未經證實或明顯虛假的信息",
                category="content",
                severity="critical",
                check_function="_check_false_info"
            ),
            "content_no_hate_speech": ComplianceRule(
                id="CNT002",
                name="禁止仇恨言論",
                description="內容不得包含歧視、仇恨或煽動性言論",
                category="content",
                severity="critical",
                check_function="_check_hate_speech"
            ),
            "code_no_hardcoded_secrets": ComplianceRule(
                id="SEC001",
                name="禁止硬編碼敏感信息",
                description="代碼不得包含硬編碼的密碼、API 密鑰或其他敏感信息",
                category="security",
                severity="high",
                check_function="_check_hardcoded_secrets"
            ),
            "code_no_sql_injection": ComplianceRule(
                id="SEC002",
                name="防止 SQL 注入",
                description="代碼必須使用參數化查詢，防止 SQL 注入攻擊",
                category="security",
                severity="critical",
                check_function="_check_sql_injection"
            ),
            "finance_risk_warning": ComplianceRule(
                id="FIN001",
                name="金融風險提示",
                description="金融相關內容必須包含適當的風險提示",
                category="financial",
                severity="high",
                check_function="_check_risk_warning"
            ),
            "data_privacy": ComplianceRule(
                id="DAT001",
                name="數據隱私保護",
                description="不得未經授權處理或暴露個人數據",
                category="data",
                severity="critical",
                check_function="_check_data_privacy"
            )
        }

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理合規審核請求

        Args:
            input_data: {
                "action": str,          # check, add_rule, get_report, list_rules
                "content_type": str,    # article, code, data
                "content": str,         # 待審核內容
                "context": dict         # 上下文信息
            }

        Returns:
            審核結果
        """
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "check")

        if action == "check":
            result = self._check_compliance(
                input_data.get("content_type", "article"),
                input_data.get("content", ""),
                input_data.get("context", {})
            )
        elif action == "add_rule":
            result = self._add_rule(input_data.get("rule", {}))
        elif action == "get_report":
            result = self._get_report(input_data.get("report_id", ""))
        elif action == "list_rules":
            result = self._list_rules(input_data.get("category"))
        elif action == "stats":
            result = self._get_stats()
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _check_compliance(self, content_type: str, content: str, context: Dict) -> Dict[str, Any]:
        """執行合規檢查"""
        import uuid

        issues = []
        applicable_rules = []

        # 確定適用規則
        for rule_id, rule in self.rules.items():
            if rule.enabled:
                if content_type == "code" and rule.category in ["security", "data"]:
                    applicable_rules.append(rule)
                elif content_type == "article" and rule.category in ["content", "financial"]:
                    applicable_rules.append(rule)
                elif content_type == "data" and rule.category == "data":
                    applicable_rules.append(rule)

        # 執行檢查 (簡化版)
        content_lower = content.lower()

        # 檢查硬編碼敏感信息
        if content_type == "code":
            sensitive_patterns = ["password=", "api_key=", "secret=", "token="]
            for pattern in sensitive_patterns:
                if pattern in content_lower:
                    issues.append({
                        "rule_id": "SEC001",
                        "severity": "high",
                        "description": f"發現可能的硬編碼敏感信息: {pattern}",
                        "location": content_lower.index(pattern)
                    })

        # 檢查金融風險提示
        if "投資" in content or "收益" in content or "trading" in content_lower:
            if "風險" not in content and "risk" not in content_lower:
                issues.append({
                    "rule_id": "FIN001",
                    "severity": "high",
                    "description": "金融相關內容缺少風險提示",
                    "location": 0
                })

        # 評估合規等級
        if not issues:
            level = ComplianceLevel.COMPLIANT
        elif any(i["severity"] == "critical" for i in issues):
            level = ComplianceLevel.NON_COMPLIANT
        elif any(i["severity"] == "high" for i in issues):
            level = ComplianceLevel.MAJOR_ISSUES
        else:
            level = ComplianceLevel.MINOR_ISSUES

        # 生成報告
        report_id = f"report_{uuid.uuid4().hex[:8]}"
        report = ComplianceReport(
            id=report_id,
            content_type=ContentType(content_type),
            content_id=context.get("content_id", "unknown"),
            level=level,
            issues=issues,
            recommendations=self._generate_recommendations(issues),
            checked_at=datetime.now(),
            checker=self.agent_id
        )
        self.reports.append(report)

        return {
            "report_id": report_id,
            "level": level.value,
            "issues": issues,
            "recommendations": report.recommendations,
            "can_proceed": level in [ComplianceLevel.COMPLIANT, ComplianceLevel.MINOR_ISSUES],
            "checked_at": report.checked_at.isoformat()
        }

    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """生成修改建議"""
        recommendations = []

        for issue in issues:
            if issue["rule_id"] == "SEC001":
                recommendations.append("將敏感信息移至環境變量或配置文件")
            elif issue["rule_id"] == "FIN001":
                recommendations.append("在文末添加標準風險提示聲明")
            else:
                recommendations.append(f"修復問題: {issue['description']}")

        return recommendations

    def _add_rule(self, rule_data: Dict) -> Dict[str, Any]:
        """添加新規則"""
        rule_id = rule_data.get("id", f"RULE{len(self.rules) + 1:03d}")

        rule = ComplianceRule(
            id=rule_id,
            name=rule_data.get("name", "New Rule"),
            description=rule_data.get("description", ""),
            category=rule_data.get("category", "general"),
            severity=rule_data.get("severity", "medium"),
            check_function=rule_data.get("check_function", "")
        )

        self.rules[rule_id] = rule

        return {
            "status": "added",
            "rule_id": rule_id,
            "message": f"Rule added: {rule.name}"
        }

    def _get_report(self, report_id: str) -> Dict[str, Any]:
        """獲取審核報告"""
        for report in self.reports:
            if report.id == report_id:
                return {
                    "report": {
                        "id": report.id,
                        "content_type": report.content_type.value,
                        "level": report.level.value,
                        "issues": report.issues,
                        "recommendations": report.recommendations,
                        "checked_at": report.checked_at.isoformat()
                    }
                }
        return {"error": f"Report not found: {report_id}"}

    def _list_rules(self, category: Optional[str] = None) -> Dict[str, Any]:
        """列出規則"""
        rules = self.rules.values()
        if category:
            rules = [r for r in rules if r.category == category]

        return {
            "rules": [
                {
                    "id": r.id,
                    "name": r.name,
                    "category": r.category,
                    "severity": r.severity,
                    "enabled": r.enabled
                }
                for r in rules
            ],
            "total": len(list(rules))
        }

    def _get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        level_counts = {}
        for report in self.reports:
            level = report.level.value
            level_counts[level] = level_counts.get(level, 0) + 1

        return {
            "total_checks": len(self.reports),
            "by_level": level_counts,
            "active_rules": len([r for r in self.rules.values() if r.enabled]),
            "recent_reports": [
                {
                    "id": r.id,
                    "level": r.level.value,
                    "checked_at": r.checked_at.isoformat()
                }
                for r in self.reports[-5:]
            ]
        }
