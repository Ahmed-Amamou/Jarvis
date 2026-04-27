from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


def print_response(text: str, title: str = "JARVIS"):
    console.print(Panel(Markdown(text), title=title, border_style="blue"))


def print_error(text: str):
    console.print(f"[red]Error:[/red] {text}")


def print_success(text: str):
    console.print(f"[green]{text}[/green]")


def print_info(text: str):
    console.print(f"[dim]{text}[/dim]")
