# All-in-One AI Organization

> 一個完整的多部門協作、動態人力資源配給的 AI 組織架構

## 🏢 組織架構

```
                         👑 User (CEO)
                              │
              ┌───────────────┼───────────────┐
              │               │               │
         🎧 Secretary    📚 Librarian
              │          (Knowledge Base)
              │
    ┌─────────┴─────────┐
    │   MANAGEMENT HUB   │
    ├────────┬──────────┤
    │Zone LAW│ Zone ARD │
    │   ⚖️   │ 🚀📋🗄️🏛️ │
    └────────┴──────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───┴───┐ ┌───┴───┐ ┌───┴───┐
│Content│ │Product│ │Trading│
│  Dev  │ │  Dev  │ │  Dev  │
└───────┘ └───────┘ └───────┘
```

## 📋 核心概念

### 1. AI 秘書 (Secretary) 🎧
- CEO 與組織的唯一接口
- 意圖路由器：理解全域需求，精確轉發指令
- 整合各部門回報

### 2. 管理中樞 (Management Hub)

#### Zone ARD (Agent Resource Development)
- **SystemPilot** 🚀: 系統營運監控
- **NewTaskManager** 📋: 新任務管理，識別開發/營運模式
- **DatabaseChecker** 🗄️: 數據庫健康監控
- **MasterArchitect** 🏛️: 架構設計與 Agent 創建

#### Zone LAW (Law & Compliance)
- **ComplianceChecker** ⚖️: 合規審計，確保所有輸出符合規範

### 3. 動態項目團隊模式 🛠️

Product Dev 和 Trading Dev 採用短期僱傭模式：

```
每個項目 = Researcher 🔍 + Foreman 👷 + Workers 🛠️
```

- **Researcher**: 研究參考資料、市場分析
- **Foreman**: 接洽需求、任務分解、監督進度
- **Workers**: 代碼開發、模組實現

### 4. Content Dev 流水線 🎙️

半流水線模式運行：

```
Content Chain: PA → CMD → Generator → ArticleKeeper
Booster Chain: KPI → Campaign
```

## 🗂️ 目錄結構

```
All-in-one/
├── config/
│   ├── organization.yaml    # 組織配置
│   └── models.yaml          # 模型配置
├── core/
│   ├── base_agent.py        # Agent 基類
│   ├── message_bus.py       # 消息總線
│   └── orchestrator.py      # 編排器
├── agents/
│   ├── executive/           # 執行層
│   │   ├── secretary.py     # CEO 秘書
│   │   └── librarian.py     # 知識庫管理
│   ├── management_hub/      # 管理中樞
│   │   ├── ard/             # ARD 區域
│   │   │   ├── system_pilot.py
│   │   │   ├── new_task_manager.py
│   │   │   ├── database_checker.py
│   │   │   └── master_architect.py
│   │   └── law/             # LAW 區域
│   │       └── compliance_checker.py
│   └── departments/         # 執行部門
│       ├── content_dev/     # 內容開發部
│       │   ├── pilots/      # 領航員
│       │   └── chains/      # 流水線
│       ├── product_dev/     # 產品開發部
│       │   ├── team_templates.py
│       │   └── project_factory.py
│       └── trading_dev/     # 交易開發部
│           ├── team_templates.py
│           └── project_factory.py
├── templates/               # 模板文件
├── utils/                   # 工具函數
├── data/                    # 數據目錄
│   ├── knowledge_base/
│   ├── logs/
│   └── reports/
└── main.py                  # 主入口
```

## 🚀 快速開始

### 安裝依賴

```bash
pip install pyyaml
```

### 運行 Demo

```bash
python main.py
```

### 基本使用

```python
from main import AIOrganization
import asyncio

async def main():
    # 初始化組織
    org = AIOrganization()
    await org.initialize()

    # 發送 CEO 指令
    result = await org.process_ceo_request("建立一個新的交易監控 Agent")

    # 創建產品項目
    project = await org.create_product_project("telegram_bot", "MyBot")

    # 創建交易項目
    trading = await org.create_trading_project("signal_alert", "Signals", "crypto")

asyncio.run(main())
```

## 📦 支援的項目類型

### Product Dev
- `article_rss`: RSS 文章聚合系統
- `polymarket`: 預測市場數據分析
- `telegram_bot`: Telegram 機器人

### Trading Dev
- `daytrade_engine`: 日內交易引擎
- `auto_trading_system`: 自動交易系統
- `signal_alert`: 交易信號提醒

## ⚠️ 風險提示

交易相關功能涉及重大風險：
- 可能損失全部投入資金
- 歷史回測結果不代表未來表現
- 使用前請確保充分了解相關風險

## 🔧 擴展指南

### 新增 Agent

1. 繼承 `BaseAgent` 基類
2. 實現 `get_system_prompt()` 和 `process()` 方法
3. 在相應目錄的 `__init__.py` 中導出

### 新增項目類型

1. 在 `project_factory.py` 的 `PROJECT_TEMPLATES` 中添加模板
2. 定義所需的模組和 Worker 數量

## 📄 License

MIT License
