# type: ignore[attr-defined]
from typing import Annotated, Optional

from enum import Enum
from random import choice

import typer
from rich.console import Console

from github_dash import version
from github_dash.app import typer_app


class Color(str, Enum):
    white = "white"
    red = "red"
    cyan = "cyan"
    magenta = "magenta"
    yellow = "yellow"
    green = "green"


app = typer.Typer(
    name="github_dash",
    help="Dash app to visualize github repository statistics such as commits per author, PRs, number of comments, etc.",
    add_completion=False,
    epilog="Made with :heart: by Leonardo Ayala",
    rich_markup_mode="rich",
)
app.add_typer(typer_app, name="run")
console = Console()


@app.command
def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(f"[yellow]github_dash[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the application's version and exit.",
    )
):
    pass


if __name__ == "__main__":
    app()
