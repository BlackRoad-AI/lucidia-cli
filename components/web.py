"""Web - Simple browser with URL bar + content"""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Label, Button, Input, RichLog
import subprocess

class WebTab(Vertical):
    """Web browser with URL bar + content pane"""
    
    DEFAULT_CSS = """
    WebTab {
        height: 100%;
    }
    WebTab > .url-bar {
        height: 3;
        border-bottom: solid gray;
    }
    WebTab > .url-bar > Input {
        width: 1fr;
    }
    WebTab > .web-content {
        height: 1fr;
        padding: 1;
        background: #111;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_url = ""
    
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Button("←", id="btn-back"),
            Button("⟳", id="btn-refresh"),
            Input(placeholder="Enter URL...", id="url-input", value="https://"),
            Button("Go", id="btn-go", variant="primary"),
            classes="url-bar"
        )
        yield RichLog(id="web-content", wrap=True, markup=True, classes="web-content")
    
    def on_mount(self) -> None:
        content = self.query_one("#web-content", RichLog)
        content.write("[bold]Lucidia Web Browser[/bold]")
        content.write("\nEnter a URL and press Go or Enter.")
        content.write("\n[dim]Tip: Try curl-able URLs for best results[/dim]")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "url-input":
            self.fetch_url(event.value)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-go":
            url = self.query_one("#url-input", Input).value
            self.fetch_url(url)
        elif event.button.id == "btn-refresh" and self.current_url:
            self.fetch_url(self.current_url)
    
    def fetch_url(self, url: str) -> None:
        if not url or url == "https://":
            return
        
        self.current_url = url
        content = self.query_one("#web-content", RichLog)
        content.clear()
        content.write(f"[dim]Loading: {url}[/dim]\n")
        
        try:
            # Use curl to fetch
            result = subprocess.run(
                ["curl", "-sL", "-m", "10", "--max-filesize", "100000", url],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0:
                text = result.stdout
                # Basic HTML stripping
                import re
                text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
                text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
                text = re.sub(r'<[^>]+>', ' ', text)
                text = re.sub(r'\s+', ' ', text)
                text = text.strip()[:5000]
                
                content.write(text if text else "[dim]Empty response[/dim]")
            else:
                content.write(f"[red]Error: {result.stderr}[/red]")
        
        except subprocess.TimeoutExpired:
            content.write("[red]Request timed out[/red]")
        except Exception as e:
            content.write(f"[red]Error: {e}[/red]")
