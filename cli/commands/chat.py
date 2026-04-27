import typer
from rich.prompt import Prompt

from cli.client import JarvisClient
from cli.output import console, print_error, print_info, print_response

app = typer.Typer(help="Chat with JARVIS")


@app.callback(invoke_without_command=True)
def chat(
    message: str = typer.Argument(None, help="Message to send"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Start interactive REPL"),
    session: str = typer.Option("default", "--session", "-s", help="Session ID"),
    url: str = typer.Option("http://localhost:8000", "--url", envvar="JARVIS_URL"),
):
    client = JarvisClient(base_url=url)

    if interactive:
        _interactive_mode(client, session)
        return

    if not message:
        print_error("Provide a message or use --interactive")
        raise typer.Exit(1)

    try:
        result = client.chat(message, session_id=session)
        print_response(result["response"])
    except Exception as e:
        print_error(str(e))
    finally:
        client.close()


def _interactive_mode(client: JarvisClient, session: str):
    print_info("JARVIS Interactive Mode (type 'exit' to quit)")
    console.print()

    while True:
        try:
            message = Prompt.ask("[bold blue]You[/bold blue]")
        except (KeyboardInterrupt, EOFError):
            break

        if message.lower() in ("exit", "quit", "q"):
            break

        if not message.strip():
            continue

        try:
            with console.status("[blue]Thinking...[/blue]"):
                result = client.chat(message, session_id=session)
            print_response(result["response"])
            console.print()
        except Exception as e:
            print_error(str(e))

    client.close()
    print_info("Goodbye!")
