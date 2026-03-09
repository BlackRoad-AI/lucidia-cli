"""Chat - Agent chat room with messages + participants"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Label, Button, Input, RichLog, ListView, ListItem
import json
import os
from datetime import datetime

CHAT_FILE = os.path.expanduser("~/.lucidia/chat_history.json")

AGENTS = ["Lucidia", "Alice", "Octavia", "Cece", "You"]

class ChatTab(Horizontal):
    """Chat room with messages + participants sidebar"""
    
    DEFAULT_CSS = """
    ChatTab {
        height: 100%;
    }
    ChatTab > .chat-main {
        width: 1fr;
    }
    ChatTab > .chat-main > RichLog {
        height: 1fr;
        border: solid gray;
        background: #111;
    }
    ChatTab > .chat-main > .chat-input-row {
        height: 3;
    }
    ChatTab > .chat-sidebar {
        width: 20;
        border-left: solid gray;
        padding: 1;
    }
    ChatTab > .chat-sidebar > .sidebar-header {
        text-style: bold;
        border-bottom: solid gray;
        padding-bottom: 1;
        margin-bottom: 1;
    }
    .agent-online { color: green; }
    .agent-offline { color: gray; }
    .msg-user { color: cyan; }
    .msg-agent { color: magenta; }
    .msg-system { color: yellow; }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = self.load_history()
    
    def load_history(self):
        if os.path.exists(CHAT_FILE):
            try:
                with open(CHAT_FILE) as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_history(self):
        os.makedirs(os.path.dirname(CHAT_FILE), exist_ok=True)
        # Keep last 100 messages
        with open(CHAT_FILE, 'w') as f:
            json.dump(self.history[-100:], f, indent=2)
    
    def compose(self) -> ComposeResult:
        yield Vertical(
            RichLog(id="chat-log", wrap=True, markup=True),
            Horizontal(
                Input(placeholder="Type message... (/council, /clear)", id="chat-input"),
                Button("Send", id="btn-send", variant="primary"),
                classes="chat-input-row"
            ),
            classes="chat-main"
        )
        yield Vertical(
            Label("👥 ONLINE", classes="sidebar-header"),
            *[Static(f"[green]● {agent}[/green]", classes="agent-online") for agent in AGENTS],
            classes="chat-sidebar"
        )
    
    def on_mount(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write("[bold]Welcome to Agent Chat[/bold]")
        log.write("[dim]Commands: /council, /clear, /history[/dim]\n")
        
        # Load recent history
        for msg in self.history[-10:]:
            self.display_message(msg, save=False)
    
    def display_message(self, msg: dict, save: bool = True) -> None:
        log = self.query_one("#chat-log", RichLog)
        
        sender = msg.get("sender", "Unknown")
        text = msg.get("text", "")
        time = msg.get("time", "")
        
        if sender == "You":
            log.write(f"[cyan][{time}] You:[/cyan] {text}")
        elif sender == "System":
            log.write(f"[yellow][{time}] {text}[/yellow]")
        else:
            log.write(f"[magenta][{time}] {sender}:[/magenta] {text}")
        
        if save:
            self.history.append(msg)
            self.save_history()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "chat-input":
            return
        
        text = event.value.strip()
        event.input.value = ""
        
        if not text:
            return
        
        now = datetime.now().strftime("%H:%M")
        
        # Handle commands
        if text.startswith("/"):
            if text == "/clear":
                self.query_one("#chat-log", RichLog).clear()
                return
            elif text == "/history":
                self.display_message({"sender": "System", "text": f"History: {len(self.history)} messages", "time": now})
                return
            elif text == "/council":
                self.display_message({"sender": "You", "text": text, "time": now})
                self.display_message({"sender": "System", "text": "Summoning the council...", "time": now})
                # Simulate agent responses
                for agent in ["Lucidia", "Alice", "Octavia", "Cece"]:
                    self.display_message({
                        "sender": agent,
                        "text": f"{agent} reporting in. Ready for council.",
                        "time": now
                    })
                return
        
        # Regular message
        self.display_message({"sender": "You", "text": text, "time": now})
        
        # Simulate agent response
        import random
        responder = random.choice(["Lucidia", "Alice", "Octavia", "Cece"])
        responses = [
            "Acknowledged.",
            "Processing your request.",
            "Interesting perspective.",
            "I'll look into that.",
            "Noted and logged.",
        ]
        self.display_message({
            "sender": responder,
            "text": random.choice(responses),
            "time": now
        })
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-send":
            inp = self.query_one("#chat-input", Input)
            if inp.value.strip():
                # Trigger input submitted
                inp.post_message(Input.Submitted(inp, inp.value))
