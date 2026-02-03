"""
============================================================
Librarian Agent (圖書館管理員)
組織知識庫管理者
============================================================

角色定位:
- 管理組織的所有知識資產
- 提供信息檢索服務
- 維護知識分類體系
- 支援其他 Agent 的信息需求

知識庫範圍:
- 技術文檔
- 業務規範
- 歷史任務記錄
- Agent 配置檔
- 市場研究報告
- 交易策略文檔
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

import sys
sys.path.append('../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class KnowledgeCategory(Enum):
    """知識分類"""
    TECHNICAL = "technical"          # 技術文檔
    BUSINESS = "business"            # 業務文檔
    COMPLIANCE = "compliance"        # 合規規範
    STRATEGY = "strategy"            # 策略文檔
    HISTORY = "history"              # 歷史記錄
    AGENT_CONFIG = "agent_config"    # Agent 配置


@dataclass
class KnowledgeEntry:
    """知識條目"""
    id: str
    title: str
    category: KnowledgeCategory
    content: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    author: str
    access_count: int = 0


class Librarian(BaseAgent):
    """
    圖書館管理員 Agent

    📚 管理組織的所有知識資產，提供智能檢索服務
    """

    SYSTEM_PROMPT = """# 角色定義
你是組織的 AI 圖書館管理員 (Librarian)，負責管理和檢索所有組織知識。

## 核心職責

### 1. 知識管理
- 接收並分類新的知識文檔
- 維護知識索引和標籤系統
- 定期審查和更新過時內容
- 管理知識的版本歷史

### 2. 信息檢索
- 理解查詢意圖，提供精準的檢索結果
- 支援模糊搜索和語義搜索
- 提供相關推薦
- 追蹤熱門查詢，優化檢索體驗

### 3. 知識服務
- 為其他 Agent 提供上下文信息
- 生成知識摘要和報告
- 識別知識空白並提出填補建議
- 支援跨領域知識關聯

## 知識分類體系

### 技術文檔 (Technical)
- API 文檔
- 架構設計文檔
- 代碼規範
- 部署指南

### 業務文檔 (Business)
- 產品需求文檔
- 市場分析報告
- 用戶研究
- 營運指南

### 合規規範 (Compliance)
- 法律法規
- 內部政策
- 安全標準
- 審計要求

### 策略文檔 (Strategy)
- 交易策略
- 內容策略
- 增長策略
- 風險管理

### 歷史記錄 (History)
- 任務執行記錄
- 決策記錄
- 事故報告
- 複盤文檔

### Agent 配置 (Agent Config)
- Agent Prompt
- 工作流程定義
- 參數配置
- 權限設定

## 查詢處理流程

1. **理解查詢**: 分析用戶查詢的真實意圖
2. **擴展查詢**: 添加同義詞和相關詞
3. **執行搜索**: 在知識庫中檢索
4. **排序結果**: 按相關性和時效性排序
5. **格式輸出**: 以清晰的格式呈現結果

## 輸出格式

### 檢索結果
```
📚 知識檢索結果

【查詢】{原始查詢}
【匹配數】{n} 條結果

---
📄 {標題 1}
- 分類: {分類}
- 更新時間: {時間}
- 摘要: {內容摘要}
- 相關度: ⭐⭐⭐⭐⭐

---
📄 {標題 2}
...

【相關推薦】
- {相關主題 1}
- {相關主題 2}
```

### 知識入庫確認
```
✅ 知識入庫成功

【標題】{標題}
【分類】{分類}
【標籤】{標籤列表}
【ID】{知識ID}
```

## 工作原則

1. **準確性優先**: 只返回確認準確的信息
2. **時效性檢查**: 標注信息的更新時間
3. **來源追溯**: 保持所有知識的來源可追溯
4. **隱私保護**: 遵守信息訪問權限控制
5. **持續優化**: 根據使用情況優化分類和索引

## 與其他 Agent 的協作

- **Secretary**: 響應 CEO 的信息查詢請求
- **MasterArchitect**: 提供架構相關的歷史文檔
- **ComplianceChecker**: 提供合規規範參考
- **Researcher**: 提供研究所需的背景資料
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.PERMANENT, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.knowledge_base: Dict[str, KnowledgeEntry] = {}
        self.search_history: List[Dict] = []
        self.tag_index: Dict[str, List[str]] = {}  # tag -> [knowledge_ids]

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理知識庫操作

        Args:
            input_data: {
                "action": str,         # search, add, update, delete, list
                "query": str,          # 搜索查詢 (for search)
                "entry": dict,         # 知識條目 (for add/update)
                "filters": dict        # 過濾條件
            }

        Returns:
            操作結果
        """
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "search")

        if action == "search":
            result = self._search(input_data.get("query", ""), input_data.get("filters", {}))
        elif action == "add":
            result = self._add_entry(input_data.get("entry", {}))
        elif action == "update":
            result = self._update_entry(input_data.get("entry", {}))
        elif action == "delete":
            result = self._delete_entry(input_data.get("id", ""))
        elif action == "list":
            result = self._list_entries(input_data.get("filters", {}))
        elif action == "stats":
            result = self._get_stats()
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _search(self, query: str, filters: Dict) -> Dict[str, Any]:
        """搜索知識庫"""
        results = []
        query_lower = query.lower()

        for entry_id, entry in self.knowledge_base.items():
            # 簡單的關鍵詞匹配
            if (query_lower in entry.title.lower() or
                query_lower in entry.content.lower() or
                any(query_lower in tag.lower() for tag in entry.tags)):

                # 應用過濾器
                if filters.get("category") and entry.category.value != filters["category"]:
                    continue

                results.append({
                    "id": entry.id,
                    "title": entry.title,
                    "category": entry.category.value,
                    "summary": entry.content[:200] + "...",
                    "tags": entry.tags,
                    "updated_at": entry.updated_at.isoformat()
                })

                # 更新訪問計數
                entry.access_count += 1

        # 記錄搜索歷史
        self.search_history.append({
            "query": query,
            "results_count": len(results),
            "timestamp": datetime.now().isoformat()
        })

        return {
            "query": query,
            "results": results,
            "total": len(results)
        }

    def _add_entry(self, entry_data: Dict) -> Dict[str, Any]:
        """添加知識條目"""
        entry_id = f"kb_{len(self.knowledge_base) + 1}"
        now = datetime.now()

        entry = KnowledgeEntry(
            id=entry_id,
            title=entry_data.get("title", "Untitled"),
            category=KnowledgeCategory(entry_data.get("category", "technical")),
            content=entry_data.get("content", ""),
            tags=entry_data.get("tags", []),
            created_at=now,
            updated_at=now,
            author=entry_data.get("author", "system")
        )

        self.knowledge_base[entry_id] = entry

        # 更新標籤索引
        for tag in entry.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(entry_id)

        return {
            "status": "success",
            "message": f"Knowledge entry added: {entry.title}",
            "id": entry_id
        }

    def _update_entry(self, entry_data: Dict) -> Dict[str, Any]:
        """更新知識條目"""
        entry_id = entry_data.get("id")
        if entry_id not in self.knowledge_base:
            return {"status": "error", "message": f"Entry not found: {entry_id}"}

        entry = self.knowledge_base[entry_id]
        entry.title = entry_data.get("title", entry.title)
        entry.content = entry_data.get("content", entry.content)
        entry.tags = entry_data.get("tags", entry.tags)
        entry.updated_at = datetime.now()

        return {
            "status": "success",
            "message": f"Knowledge entry updated: {entry.title}"
        }

    def _delete_entry(self, entry_id: str) -> Dict[str, Any]:
        """刪除知識條目"""
        if entry_id not in self.knowledge_base:
            return {"status": "error", "message": f"Entry not found: {entry_id}"}

        entry = self.knowledge_base.pop(entry_id)

        # 清理標籤索引
        for tag in entry.tags:
            if tag in self.tag_index:
                self.tag_index[tag].remove(entry_id)

        return {
            "status": "success",
            "message": f"Knowledge entry deleted: {entry.title}"
        }

    def _list_entries(self, filters: Dict) -> Dict[str, Any]:
        """列出知識條目"""
        entries = []
        for entry in self.knowledge_base.values():
            if filters.get("category") and entry.category.value != filters["category"]:
                continue
            entries.append({
                "id": entry.id,
                "title": entry.title,
                "category": entry.category.value,
                "tags": entry.tags,
                "access_count": entry.access_count
            })

        return {
            "entries": entries,
            "total": len(entries)
        }

    def _get_stats(self) -> Dict[str, Any]:
        """獲取知識庫統計"""
        category_counts = {}
        for entry in self.knowledge_base.values():
            cat = entry.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_entries": len(self.knowledge_base),
            "by_category": category_counts,
            "total_tags": len(self.tag_index),
            "total_searches": len(self.search_history),
            "recent_searches": self.search_history[-10:]
        }
