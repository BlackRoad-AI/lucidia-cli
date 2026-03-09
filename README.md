# LUCIDIA CLI

> A whole computer in a computer, and a whole web engine.
> ⬥ BlackRoad OS, Inc.

## Structure
```
lucidia-cli/
├── lucidia.py              # Main TUI app
├── components/
│   ├── __init__.py         # Package exports
│   ├── web_engine.py       # Terminal web browser
│   ├── virtual_fs.py       # Sandboxed filesystem
│   ├── agents.py           # Ollama AI agents
│   ├── apps.py             # Mini applications
│   └── process_mgr.py      # Background tasks
├── config/
│   └── settings.json       # User settings
└── README.md
```

## Components

### Web Engine (`web_engine.py`)
- HTML to Rich markup parser
- Link extraction and following
- History navigation
- DuckDuckGo search

### Virtual FS (`virtual_fs.py`)
- Sandboxed at `~/.lucidia/vfs`
- Standard operations: ls, cd, cat, write, mkdir, rm
- Persistent across sessions

### Agents (`agents.py`)
- Ollama-powered AI agents
- Personalities: lucidia, alice, octavia, cece, operator
- Council mode for multi-agent discussion

### Apps (`apps.py`)
- calc: Safe calculator
- btc/eth: Crypto prices
- fortune: Random wisdom
- weather: wttr.in integration
- time/date/unix: Clock utilities
- whoami/neofetch: System info

### Process Manager (`process_mgr.py`)
- Async task spawning
- PID tracking
- ps/kill commands

## Keybindings

| Key | Tab |
|-----|-----|
| Ctrl+1 | Shell |
| Ctrl+2 | Web |
| Ctrl+3 | Files |
| Ctrl+4 | Agents |
| Ctrl+5 | Apps |
| Ctrl+Q | Quit |

## Run
```bash
cd ~/lucidia-cli
python lucidia.py
```

## Dependencies
```bash
pip install textual rich
# Ollama running locally for agents
```

---

*"The road is black, but the way is clear."*
