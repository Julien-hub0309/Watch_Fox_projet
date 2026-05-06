from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel

custom_theme = Theme({
    "info": "bold cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "target": "bold magenta"
})

console = Console(theme=custom_theme)

def print_banner():
    banner = Panel.fit(
        "[bold cyan]🦊 Justradamus Osint Tool[/bold cyan]\n[dim]Intelligence & Investigation Framework[/dim]",
        border_style="cyan"
    )
    console.print(banner)

def print_error(msg): console.print(f"[error][!][/error] {msg}")
def print_success(msg): console.print(f"[success][+][/success] {msg}")