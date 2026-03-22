# All-in-one
1人團隊 — One-person team powered by multi-agent AI

## Architecture

Hierarchical multi-agent system with an **orchestrator** that decomposes tasks and delegates to four **specialist agents**, each running in its own context window:

```
Developer
    │
    ▼
┌─────────────────────┐
│  Orchestrator Agent  │
│  - Task decomposition│
│  - Work distribution │
│  - Result synthesis  │
│  - Quality control   │
└──┬──┬──┬──┬─────────┘
   │  │  │  │
   ▼  ▼  ▼  ▼
 ┌──┐┌──┐┌──┐┌──┐
 │A ││B ││C ││D │  ← Specialist agents
 └──┘└──┘└──┘└──┘
  │   │   │   │
  ▼   ▼   ▼   ▼
 [Context windows]
        │
        ▼
 Integrated output
```

| Specialist | Role |
|---|---|
| A — Architect | Architecture and design |
| B — Implementer | Implementation and coding |
| C — Tester | Testing and validation |
| D — Reviewer | Review and documentation |

## Usage

```bash
export ANTHROPIC_API_KEY=sk-...
pip install -e .
aio "Build a REST API for a todo app"
```

## Configuration

| Env var | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Required |
| `AIO_ORCHESTRATOR_MODEL` | `claude-sonnet-4-20250514` | Model for orchestrator |
| `AIO_SPECIALIST_MODEL` | `claude-haiku-4-5-20251001` | Model for specialists |
| `AIO_MAX_PARALLEL` | `4` | Max parallel specialist tasks |
