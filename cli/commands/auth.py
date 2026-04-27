import webbrowser

import typer

from cli.client import JarvisClient
from cli.output import print_error, print_info, print_success

app = typer.Typer(help="Authentication management")


@app.command()
def login(
    url: str = typer.Option("http://localhost:8000", "--url", envvar="JARVIS_URL"),
):
    """Authenticate with Google (opens browser)."""
    auth_url = f"{url}/auth/google"
    print_info(f"Opening browser for Google authentication...")
    print_info(f"If the browser doesn't open, visit: {auth_url}")
    webbrowser.open(auth_url)


@app.command()
def status(
    url: str = typer.Option("http://localhost:8000", "--url", envvar="JARVIS_URL"),
):
    """Check authentication status."""
    client = JarvisClient(base_url=url)
    try:
        result = client.auth_status()
        if result.get("google_authenticated"):
            print_success("Google: Authenticated")
        else:
            print_error("Google: Not authenticated. Run 'jarvis auth login'")
    except Exception as e:
        print_error(str(e))
    finally:
        client.close()
