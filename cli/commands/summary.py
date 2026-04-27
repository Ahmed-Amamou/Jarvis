import typer

from cli.client import JarvisClient
from cli.output import print_error, print_response

app = typer.Typer(help="Get quick summaries")


@app.callback(invoke_without_command=True)
def summary(
    period: str = typer.Argument("today", help="Period: today or week"),
    url: str = typer.Option("http://localhost:8000", "--url", envvar="JARVIS_URL"),
):
    client = JarvisClient(base_url=url)

    prompts = {
        "today": "Give me a summary of today's meetings and any emails I need to respond to.",
        "week": "Give me an overview of my schedule for this week and any important emails.",
    }

    prompt = prompts.get(period)
    if not prompt:
        print_error(f"Unknown period: {period}. Use 'today' or 'week'.")
        raise typer.Exit(1)

    try:
        result = client.chat(prompt)
        print_response(result["response"], title=f"Summary — {period.title()}")
    except Exception as e:
        print_error(str(e))
    finally:
        client.close()
