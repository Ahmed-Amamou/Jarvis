import typer

from cli.commands import auth, chat, schedule, summary

app = typer.Typer(
    name="jarvis",
    help="JARVIS — Your AI Assistant for Gmail & Calendar",
    no_args_is_help=True,
)

app.add_typer(chat.app, name="chat")
app.add_typer(summary.app, name="summary")
app.add_typer(auth.app, name="auth")
app.add_typer(schedule.app, name="schedule")


@app.command()
def status(
    url: str = typer.Option("http://localhost:8000", "--url", envvar="JARVIS_URL"),
):
    """Show system status."""
    from cli.client import JarvisClient
    from cli.output import console, print_error

    client = JarvisClient(base_url=url)
    try:
        health = client.health()
        auth_info = client.auth_status()

        console.print(f"[bold]JARVIS Status[/bold]")
        console.print(f"  Gateway:  [green]OK[/green]")
        console.print(
            f"  Ollama:   [{'green' if health['ollama'] else 'red'}]"
            f"{'Connected' if health['ollama'] else 'Disconnected'}[/]"
        )
        console.print(
            f"  Google:   [{'green' if auth_info['google_authenticated'] else 'yellow'}]"
            f"{'Authenticated' if auth_info['google_authenticated'] else 'Not authenticated'}[/]"
        )
    except Exception as e:
        print_error(f"Cannot reach JARVIS gateway: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    app()
