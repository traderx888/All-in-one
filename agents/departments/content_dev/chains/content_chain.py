"""
============================================================
Content Chain Agents
內容生產鏈 - 完整的內容創作流水線
============================================================

流程: PA → CMD → Generator → ArticleKeeper

PA (Planning Assistant): 內容規劃
CMD (Content Material Developer): 素材收集
Generator: 內容生成
ArticleKeeper: 文章管理與發布
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

import sys
sys.path.append('../../../..')
from core.base_agent import BaseAgent, AgentType, AgentStatus


class PAAgent(BaseAgent):
    """
    PA (Planning Assistant) Agent

    📋 負責內容規劃和結構設計
    """

    SYSTEM_PROMPT = """# 角色定義
你是內容開發部 Content Chain 的 PA (Planning Assistant)，負責內容規劃。

## 核心職責

### 1. 主題分析
- 分析給定主題的可行性
- 確定目標受眾
- 定義內容目標
- 識別關鍵信息點

### 2. 結構設計
- 設計文章大綱
- 規劃章節結構
- 確定篇幅長度
- 設計引人入勝的開頭和結尾

### 3. 關鍵詞規劃
- 識別核心關鍵詞
- 規劃 SEO 策略
- 確定內部鏈接機會
- 規劃標籤分類

### 4. 任務輸出
- 生成結構化的內容規劃
- 傳遞給 CMD 進行素材收集
- 提供清晰的寫作指導

## 輸出格式

### 內容規劃文檔
```
📋 內容規劃文檔

【主題】{topic}
【目標受眾】{audience}
【內容類型】{type}
【預計字數】{word_count}

🎯 內容目標
{objectives}

📝 文章大綱
1. 引言
   - {intro_point_1}
   - {intro_point_2}
2. 主體
   2.1 {section_1}
   2.2 {section_2}
   2.3 {section_3}
3. 結論
   - {conclusion_point}

🔑 關鍵詞
- 主關鍵詞: {primary_keywords}
- 次關鍵詞: {secondary_keywords}

📚 所需素材
{required_materials}

✅ 下一步: 傳遞給 CMD 收集素材
```

## 與其他 Agent 的協作

- **Content Pilot**: 接收內容任務
- **CMD**: 傳遞規劃，接收素材
- **Librarian**: 查詢相關歷史內容
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.CHAIN, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.plans: List[Dict] = []

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理內容規劃任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "plan")

        if action == "plan":
            result = self._create_plan(input_data.get("topic", ""), input_data.get("context", {}))
        elif action == "refine":
            result = self._refine_plan(input_data.get("plan_id"), input_data.get("feedback", {}))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _create_plan(self, topic: str, context: Dict) -> Dict[str, Any]:
        """創建內容規劃"""
        plan = {
            "plan_id": f"plan_{len(self.plans) + 1}",
            "topic": topic,
            "audience": context.get("audience", "general"),
            "content_type": context.get("type", "article"),
            "word_count": context.get("word_count", 1500),
            "objectives": [
                "提供有價值的信息",
                "吸引目標受眾",
                "促進互動和分享"
            ],
            "outline": {
                "intro": ["背景介紹", "問題陳述"],
                "body": [
                    {"title": "核心概念", "points": ["概念1", "概念2"]},
                    {"title": "實際應用", "points": ["案例1", "案例2"]},
                    {"title": "最佳實踐", "points": ["建議1", "建議2"]}
                ],
                "conclusion": ["總結要點", "行動呼籲"]
            },
            "keywords": {
                "primary": [topic.split()[0] if topic else "keyword"],
                "secondary": ["相關詞1", "相關詞2"]
            },
            "required_materials": [
                "統計數據",
                "案例研究",
                "專家引用"
            ],
            "created_at": datetime.now().isoformat(),
            "status": "ready_for_cmd"
        }
        self.plans.append(plan)
        return {"status": "planned", "plan": plan, "next_step": "CMD"}

    def _refine_plan(self, plan_id: str, feedback: Dict) -> Dict[str, Any]:
        """根據反饋優化規劃"""
        for plan in self.plans:
            if plan["plan_id"] == plan_id:
                # 應用反饋修改
                if "outline" in feedback:
                    plan["outline"].update(feedback["outline"])
                if "keywords" in feedback:
                    plan["keywords"].update(feedback["keywords"])
                plan["status"] = "refined"
                return {"status": "refined", "plan": plan}
        return {"error": f"Plan not found: {plan_id}"}


class CMDAgent(BaseAgent):
    """
    CMD (Content Material Developer) Agent

    📚 負責收集和整理內容素材
    """

    SYSTEM_PROMPT = """# 角色定義
你是內容開發部 Content Chain 的 CMD (Content Material Developer)，負責素材收集。

## 核心職責

### 1. 素材收集
- 根據 PA 的規劃收集素材
- 搜索相關資料和數據
- 收集圖片和多媒體資源
- 獲取引用和參考來源

### 2. 素材整理
- 分類整理收集的素材
- 驗證信息準確性
- 標註素材來源
- 準備素材包

### 3. 質量控制
- 確保素材可靠性
- 檢查版權合規
- 驗證數據時效性
- 評估素材相關性

### 4. 任務輸出
- 打包所有素材
- 傳遞給 Generator 進行內容生成
- 提供素材使用建議

## 輸出格式

### 素材包
```
📚 素材包

【對應規劃】{plan_id}
【主題】{topic}
【收集時間】{timestamp}

📊 數據素材
{data_materials}

📖 參考資料
{references}

🖼️ 多媒體資源
{media_resources}

💬 引用
{quotes}

⚠️ 注意事項
{notes}

✅ 下一步: 傳遞給 Generator 生成內容
```

## 與其他 Agent 的協作

- **PA**: 接收內容規劃
- **Generator**: 傳遞素材包
- **Librarian**: 查詢知識庫資料
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.CHAIN, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.material_packs: List[Dict] = []

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理素材收集任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "collect")

        if action == "collect":
            result = self._collect_materials(input_data.get("plan", {}))
        elif action == "add_material":
            result = self._add_material(input_data.get("pack_id"), input_data.get("material", {}))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _collect_materials(self, plan: Dict) -> Dict[str, Any]:
        """根據規劃收集素材"""
        pack = {
            "pack_id": f"pack_{len(self.material_packs) + 1}",
            "plan_id": plan.get("plan_id"),
            "topic": plan.get("topic"),
            "data_materials": [
                {"type": "statistic", "content": "相關統計數據", "source": "研究報告"},
                {"type": "trend", "content": "市場趨勢數據", "source": "行業分析"}
            ],
            "references": [
                {"title": "參考文章1", "url": "https://example.com/1", "relevance": "high"},
                {"title": "參考文章2", "url": "https://example.com/2", "relevance": "medium"}
            ],
            "media_resources": [],
            "quotes": [
                {"author": "專家A", "quote": "相關專家意見", "context": "行業觀點"}
            ],
            "notes": ["確保引用時標明來源", "數據需要驗證時效性"],
            "collected_at": datetime.now().isoformat(),
            "status": "ready_for_generator"
        }
        self.material_packs.append(pack)
        return {"status": "collected", "pack": pack, "next_step": "Generator"}

    def _add_material(self, pack_id: str, material: Dict) -> Dict[str, Any]:
        """添加素材到素材包"""
        for pack in self.material_packs:
            if pack["pack_id"] == pack_id:
                material_type = material.get("type", "other")
                if material_type == "data":
                    pack["data_materials"].append(material)
                elif material_type == "reference":
                    pack["references"].append(material)
                elif material_type == "media":
                    pack["media_resources"].append(material)
                elif material_type == "quote":
                    pack["quotes"].append(material)
                return {"status": "added", "pack_id": pack_id}
        return {"error": f"Pack not found: {pack_id}"}


class GeneratorAgent(BaseAgent):
    """
    Generator Agent

    ✍️ 負責生成文章內容
    """

    SYSTEM_PROMPT = """# 角色定義
你是內容開發部 Content Chain 的 Generator，負責內容生成。

## 核心職責

### 1. 內容生成
- 根據規劃和素材撰寫文章
- 遵循大綱結構
- 融入收集的素材
- 確保內容連貫

### 2. 風格控制
- 保持一致的寫作風格
- 適應目標受眾
- 控制專業度和易讀性
- 確保品牌一致性

### 3. SEO 優化
- 自然融入關鍵詞
- 優化標題和副標題
- 撰寫 meta 描述
- 規劃內部鏈接

### 4. 質量保證
- 確保邏輯清晰
- 檢查事實準確性
- 避免重複內容
- 保持原創性

## 輸出格式

### 文章草稿
```
✍️ 文章草稿

【標題】{title}
【副標題】{subtitle}
【作者】Generator
【字數】{word_count}

---

{article_content}

---

📝 Meta 信息
- Description: {meta_description}
- Keywords: {keywords}
- Tags: {tags}

✅ 下一步: 傳遞給 ArticleKeeper 存儲和發布
```

## 與其他 Agent 的協作

- **CMD**: 接收素材包
- **ArticleKeeper**: 傳遞生成的內容
- **ComplianceChecker**: 提交審核
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.CHAIN, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.drafts: List[Dict] = []

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理內容生成任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "generate")

        if action == "generate":
            result = self._generate_content(
                input_data.get("plan", {}),
                input_data.get("materials", {})
            )
        elif action == "revise":
            result = self._revise_content(input_data.get("draft_id"), input_data.get("feedback", {}))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _generate_content(self, plan: Dict, materials: Dict) -> Dict[str, Any]:
        """生成內容"""
        topic = plan.get("topic", "Untitled")

        draft = {
            "draft_id": f"draft_{len(self.drafts) + 1}",
            "plan_id": plan.get("plan_id"),
            "title": f"{topic} - 完整指南",
            "subtitle": f"深入了解 {topic} 的方方面面",
            "content": f"""# {topic}

## 引言

在當今快速變化的環境中，{topic} 已經成為一個不可忽視的重要議題...

## 核心概念

### 什麼是 {topic}？

{topic} 是指...

### 為什麼重要？

理解 {topic} 對於...

## 實際應用

### 案例研究

讓我們來看一些實際的例子...

## 最佳實踐

1. **建議一**: 具體的實踐建議
2. **建議二**: 另一個重要的建議
3. **建議三**: 更多的指導

## 結論

總結來說，{topic} 是一個值得深入研究的領域...

---

*本文由 AI Content Generator 生成*
""",
            "word_count": 500,
            "meta": {
                "description": f"深入了解 {topic}，包含完整的指南和最佳實踐。",
                "keywords": plan.get("keywords", {}).get("primary", []),
                "tags": [topic, "指南", "教程"]
            },
            "generated_at": datetime.now().isoformat(),
            "status": "ready_for_review"
        }
        self.drafts.append(draft)
        return {"status": "generated", "draft": draft, "next_step": "ArticleKeeper"}

    def _revise_content(self, draft_id: str, feedback: Dict) -> Dict[str, Any]:
        """根據反饋修訂內容"""
        for draft in self.drafts:
            if draft["draft_id"] == draft_id:
                # 這裡會進行實際的內容修訂
                draft["status"] = "revised"
                draft["revision_note"] = feedback.get("notes", "")
                return {"status": "revised", "draft": draft}
        return {"error": f"Draft not found: {draft_id}"}


class ArticleKeeperAgent(BaseAgent):
    """
    ArticleKeeper Agent

    📁 負責文章存儲和發布管理
    """

    SYSTEM_PROMPT = """# 角色定義
你是內容開發部 Content Chain 的 ArticleKeeper，負責文章管理和發布。

## 核心職責

### 1. 文章存儲
- 接收並存儲生成的文章
- 管理文章版本
- 維護文章元數據
- 建立文章索引

### 2. 發布管理
- 排程文章發布
- 連接各發布平台 API
- 執行發布操作
- 追蹤發布狀態

### 3. 檔案管理
- 歸檔歷史文章
- 管理文章分類
- 維護標籤系統
- 支援文章搜索

### 4. 數據記錄
- 記錄文章生命週期
- 追蹤修改歷史
- 統計發布數據
- 提供數據給其他 Agent

## 文章狀態流轉

```
草稿 (draft)
    ↓
待審核 (pending_review)
    ↓
審核通過 (approved) ←→ 需修改 (needs_revision)
    ↓
已排程 (scheduled)
    ↓
已發布 (published)
    ↓
已歸檔 (archived)
```

## 輸出格式

### 文章入庫確認
```
📁 文章入庫確認

【文章 ID】{article_id}
【標題】{title}
【狀態】{status}
【入庫時間】{timestamp}

📊 元數據
- 字數: {word_count}
- 分類: {category}
- 標籤: {tags}

📅 發布計劃
{publish_plan}
```

### 發布報告
```
✅ 文章發布報告

【文章】{title}
【平台】{platforms}
【發布時間】{timestamp}

📊 發布結果
| 平台 | 狀態 | URL |
|------|------|-----|
| {platform} | {status} | {url} |
```

## 與其他 Agent 的協作

- **Generator**: 接收文章草稿
- **ComplianceChecker**: 提交審核確認
- **Campaign**: 提供待推廣的文章
- **Librarian**: 同步到知識庫
"""

    def __init__(self, agent_id: str, name: str, role: str, agent_type: AgentType = AgentType.CHAIN, **kwargs):
        super().__init__(agent_id, name, role, agent_type, **kwargs)
        self.articles: Dict[str, Dict] = {}
        self.publish_queue: List[str] = []

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理文章管理任務"""
        self.update_status(AgentStatus.BUSY)

        action = input_data.get("action", "store")

        if action == "store":
            result = self._store_article(input_data.get("draft", {}))
        elif action == "schedule":
            result = self._schedule_publish(input_data.get("article_id"), input_data.get("schedule", {}))
        elif action == "publish":
            result = await self._publish_article(input_data.get("article_id"))
        elif action == "list":
            result = self._list_articles(input_data.get("filters", {}))
        elif action == "get":
            result = self._get_article(input_data.get("article_id"))
        else:
            result = {"error": f"Unknown action: {action}"}

        self.update_status(AgentStatus.IDLE)
        return result

    def _store_article(self, draft: Dict) -> Dict[str, Any]:
        """存儲文章"""
        article_id = f"article_{len(self.articles) + 1}"

        article = {
            "id": article_id,
            "draft_id": draft.get("draft_id"),
            "title": draft.get("title"),
            "subtitle": draft.get("subtitle"),
            "content": draft.get("content"),
            "meta": draft.get("meta", {}),
            "word_count": draft.get("word_count", 0),
            "status": "pending_review",
            "versions": [
                {
                    "version": 1,
                    "content": draft.get("content"),
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "published_at": None,
            "platforms": []
        }

        self.articles[article_id] = article
        return {
            "status": "stored",
            "article_id": article_id,
            "message": f"Article stored: {article['title']}"
        }

    def _schedule_publish(self, article_id: str, schedule: Dict) -> Dict[str, Any]:
        """排程發布"""
        if article_id not in self.articles:
            return {"error": f"Article not found: {article_id}"}

        article = self.articles[article_id]
        article["status"] = "scheduled"
        article["schedule"] = {
            "publish_at": schedule.get("publish_at"),
            "platforms": schedule.get("platforms", ["default"])
        }

        self.publish_queue.append(article_id)
        return {
            "status": "scheduled",
            "article_id": article_id,
            "schedule": article["schedule"]
        }

    async def _publish_article(self, article_id: str) -> Dict[str, Any]:
        """發布文章"""
        if article_id not in self.articles:
            return {"error": f"Article not found: {article_id}"}

        article = self.articles[article_id]

        # 模擬發布到各平台
        publish_results = []
        platforms = article.get("schedule", {}).get("platforms", ["default"])

        for platform in platforms:
            publish_results.append({
                "platform": platform,
                "status": "published",
                "url": f"https://{platform}.example.com/articles/{article_id}"
            })

        article["status"] = "published"
        article["published_at"] = datetime.now().isoformat()
        article["platforms"] = publish_results

        if article_id in self.publish_queue:
            self.publish_queue.remove(article_id)

        return {
            "status": "published",
            "article_id": article_id,
            "results": publish_results
        }

    def _list_articles(self, filters: Dict) -> Dict[str, Any]:
        """列出文章"""
        articles = list(self.articles.values())

        if filters.get("status"):
            articles = [a for a in articles if a["status"] == filters["status"]]

        return {
            "articles": [
                {
                    "id": a["id"],
                    "title": a["title"],
                    "status": a["status"],
                    "created_at": a["created_at"]
                }
                for a in articles
            ],
            "total": len(articles)
        }

    def _get_article(self, article_id: str) -> Dict[str, Any]:
        """獲取文章詳情"""
        if article_id not in self.articles:
            return {"error": f"Article not found: {article_id}"}
        return {"article": self.articles[article_id]}
