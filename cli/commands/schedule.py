import typer
from rich.table import Table

from cli.client import JarvisClient
from cli.output import console, print_error, print_success

app = typer.Typer(help="Manage scheduled jobs")


@app.command("list")
def list_schedules(
    url: str = typer.Option("http://localhost:8000", "--url", envvar="JARVIS_URL"),
):
    """List all scheduled jobs."""
    client = JarvisClient(base_url=url)
    try:
        jobs = client.list_schedules()
        if not jobs:
            console.print("[dim]No scheduled jobs.[/dim]")
            return

        table = Table(title="Scheduled Jobs")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Next Run", style="yellow")

        for job in jobs:
            table.add_row(job["id"], job["name"], job.get("next_run", "—"))

        console.print(table)
    except Exception as e:
        print_error(str(e))
    finally:
        client.close()


@app.command("create")
def create_schedule(
    name: str = typer.Argument(help="Job name"),
    cron: str = typer.Argument(help="Cron expression (5 fields: min hour day month dow)"),
    job_type: str = typer.Option(
        "morning_summary",
        "--type", "-t",
        help="Job type: morning_summary, meeting_reminder, email_check",
    ),
    url: str = typer.Option("http://localhost:8000", "--url", envvar="JARVIS_URL"),
):
    """Create or update a scheduled job."""
    client = JarvisClient(base_url=url)
    try:
        result = client.create_schedule(name, cron, job_type)
        if "error" in result:
            print_error(result["error"])
        else:
            print_success(f"Schedule '{name}' created: {cron}")
    except Exception as e:
        print_error(str(e))
    finally:
        client.close()


@app.command("delete")
def delete_schedule(
    job_id: str = typer.Argument(help="Job ID to delete"),
    url: str = typer.Option("http://localhost:8000", "--url", envvar="JARVIS_URL"),
):
    """Delete a scheduled job."""
    client = JarvisClient(base_url=url)
    try:
        result = client.delete_schedule(job_id)
        if "error" in result:
            print_error(result["error"])
        else:
            print_success(f"Schedule '{job_id}' deleted.")
    except Exception as e:
        print_error(str(e))
    finally:
        client.close()
