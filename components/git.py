"""Git - Repository status with branches + commits"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Static, Label, Button, DataTable, RichLog, Input
import subprocess
import os

class GitTab(Container):
    """Git with 2x2 grid: status, branches, commits, actions"""
    
    DEFAULT_CSS = """
    GitTab {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
        padding: 1;
        height: 100%;
    }
    GitTab > .git-panel {
        border: solid gray;
        padding: 1;
    }
    GitTab > .git-panel > .panel-header {
        text-style: bold;
        border-bottom: solid gray;
        padding-bottom: 1;
        margin-bottom: 1;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo_path = os.getcwd()
    
    def compose(self) -> ComposeResult:
        # Status panel
        yield Vertical(
            Label("📊 STATUS", classes="panel-header"),
            Static("", id="git-status"),
            classes="git-panel"
        )
        # Branch panel
        yield Vertical(
            Label("🌿 BRANCHES", classes="panel-header"),
            Static("", id="git-branches"),
            classes="git-panel"
        )
        # Commits panel
        yield Vertical(
            Label("📝 RECENT COMMITS", classes="panel-header"),
            Static("", id="git-commits"),
            classes="git-panel"
        )
        # Actions panel
        yield Vertical(
            Label("⚡ ACTIONS", classes="panel-header"),
            Horizontal(
                Button("Status", id="btn-git-status", variant="primary"),
                Button("Pull", id="btn-git-pull"),
                Button("Fetch", id="btn-git-fetch"),
            ),
            Input(placeholder="Repository path...", id="git-path", value=self.repo_path),
            classes="git-panel"
        )
    
    def on_mount(self) -> None:
        self.refresh_all()
    
    def refresh_all(self) -> None:
        self.refresh_status()
        self.refresh_branches()
        self.refresh_commits()
    
    def git_cmd(self, args: list) -> str:
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path] + args,
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
        except Exception as e:
            return f"Error: {e}"
    
    def refresh_status(self) -> None:
        status = self.query_one("#git-status", Static)
        
        # Check if git repo
        result = self.git_cmd(["rev-parse", "--git-dir"])
        if "Error" in result:
            status.update("[red]Not a git repository[/red]")
            return
        
        # Get status
        branch = self.git_cmd(["branch", "--show-current"])
        changes = self.git_cmd(["status", "--porcelain"])
        
        change_count = len(changes.split("\n")) if changes else 0
        
        status.update(
            f"Branch: [bold]{branch}[/bold]\n"
            f"Changes: {change_count} files\n"
            f"Path: {self.repo_path}"
        )
    
    def refresh_branches(self) -> None:
        branches = self.query_one("#git-branches", Static)
        result = self.git_cmd(["branch", "-a", "--format=%(refname:short)"])
        
        if "Error" not in result:
            branch_list = result.split("\n")[:10]
            branches.update("\n".join([f"• {b}" for b in branch_list if b]))
        else:
            branches.update("[dim]No branches[/dim]")
    
    def refresh_commits(self) -> None:
        commits = self.query_one("#git-commits", Static)
        result = self.git_cmd(["log", "--oneline", "-10"])
        
        if "Error" not in result:
            commits.update(result if result else "[dim]No commits[/dim]")
        else:
            commits.update("[dim]No commits[/dim]")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-git-status":
            self.refresh_all()
        elif event.button.id == "btn-git-pull":
            result = self.git_cmd(["pull"])
            self.notify(result[:100], title="Git Pull")
            self.refresh_all()
        elif event.button.id == "btn-git-fetch":
            result = self.git_cmd(["fetch", "--all"])
            self.notify("Fetch complete", title="Git Fetch")
            self.refresh_all()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "git-path":
            path = event.value.strip()
            if os.path.isdir(path):
                self.repo_path = path
                self.refresh_all()
            else:
                self.notify("Invalid path", title="Git")
