# Installed Claude Code Skills

This document tracks the Claude Code skills installed for this project.

## claude-mem

**Version:** 6.5.0
**Repository:** https://github.com/thedotmack/claude-mem
**Installation Date:** 2026-02-12
**Installation Location:** `~/.config/claude-code/skills/claude-mem/`

### Description

Persistent memory compression system built for Claude Code that enables context preservation across sessions.

### Features

- 🧠 **Persistent Memory** - Context survives across sessions
- 📊 **Progressive Disclosure** - Layered memory retrieval with token cost visibility
- 🔍 **Skill-Based Search** - Query project history with mem-search skill
- 🖥️ **Web Viewer UI** - Real-time memory stream at http://localhost:37777
- 💻 **Claude Desktop Skill** - Search memory from Claude Desktop conversations
- 🔒 **Privacy Control** - Use `<private>` tags to exclude sensitive content
- ⚙️ **Context Configuration** - Fine-grained control over context injection
- 🤖 **Automatic Operation** - No manual intervention required
- 🔗 **Citations** - Reference past observations with IDs

### Installation Method

```bash
mkdir -p ~/.config/claude-code/skills
cd ~/.config/claude-code/skills
git clone https://github.com/thedotmack/claude-mem.git
```

### Usage

After restarting Claude Code:
- Context is automatically captured and preserved
- Access web viewer at: http://localhost:37777
- Use `/mem-search` skill to query project history
- MCP search tools available for memory queries

### Configuration

Settings managed in: `~/.claude-mem/settings.json`
Documentation: https://docs.claude-mem.ai/

### System Requirements

- Node.js 18.0.0 or higher
- Bun (auto-installed if missing)
- SQLite 3 (bundled)
- uv (auto-installed if missing)

### License

GNU Affero General Public License v3.0 (AGPL-3.0)
