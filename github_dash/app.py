import os
from datetime import datetime, timezone

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.io as pio
import typer
from dash import Input, Output, Patch, State, clientside_callback
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url

from .github_stats import data_lock, update_data
from .layout import set_layout

typer_app = typer.Typer(
    no_args_is_help=True, epilog="Made with :heart: by Leonardo Ayala"
)

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
dash_app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css],
)

CSV_FILE = None
REPO = None
START_DATE = None
END_DATE = None
INTERVAL: int = None


def run_app():
    global INTERVAL
    set_layout(dash_app, interval=INTERVAL)
    dash_app.run_server(debug=False, use_reloader=False)


def load_data():
    global CSV_FILE, data_lock
    with data_lock:
        data = {
            "commits": pd.read_csv(f"{CSV_FILE}_commits.csv"),
            "prs": pd.read_csv(f"{CSV_FILE}_prs.csv"),
            "issues": pd.read_csv(f"{CSV_FILE}_issues.csv"),
            "comments": pd.read_csv(f"{CSV_FILE}_comments.csv"),
        }
    return data


def data_ok(df: pd.DataFrame):
    return ~df.empty


@dash_app.callback(
    Output("spinner", "children"), Input("interval-component", "n_intervals")
)
def update_github_data(n_intervals):
    update_data(
        repo_name=REPO, start_date=START_DATE, end_date=END_DATE, csv_file=CSV_FILE
    )
    now = datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
    return f"Data reloaded on {now}"


@dash_app.callback(
    Output("commits-graph", "figure"),
    Output("prs-graph", "figure"),
    Output("issues-graph", "figure"),
    Output("comments-graph", "figure"),
    Input("interval-component", "n_intervals"),
    State(ThemeChangerAIO.ids.radio("theme"), "value"),
    State("switch", "value"),
    prevent_initial_call=False,
)
def update_graphs(n_intervals, theme, color_mode_switch_on):
    data = load_data()

    # update theme
    theme_name = template_from_url(theme)
    template_name = theme_name if color_mode_switch_on else theme_name + "_dark"

    # instantiate figures
    commits_fig = {}
    prs_fig = {}
    issues_fig = {}
    comments_fig = {}

    # Commit statistics
    df_commits = data["commits"]
    if data_ok(df_commits):
        df_commits = df_commits.groupby("author").sum().reset_index()
        df_commits = df_commits.melt(
            id_vars=["author"],
            var_name="Type",
            value_name="Count",
            value_vars=["insertions", "deletions"],
        )
        commits_fig = px.bar(
            data_frame=df_commits,
            x="author",
            y="Count",
            color="Type",
            template=template_name,
            title="Number of commits per Author",
        )

    # PR statistics
    df_prs = data["prs"]
    if data_ok(df_prs):
        df_prs = (
            df_prs.groupby(["author"])
            .agg({"type": "size", "merged": "sum"})
            .reset_index()
        )
        df_prs.rename({"type": "opened"}, inplace=True, axis=1)
        df_prs = df_prs.melt(
            id_vars=["author"],
            var_name="Type",
            value_name="Count",
            value_vars=["opened", "merged"],
        )
        prs_fig = px.bar(
            data_frame=df_prs,
            x="author",
            y="Count",
            color="Type",
            template=template_name,
            title="Number of PRs per Author",
        )

    # Issue statistics
    df_issues = data["issues"]
    if data_ok(df_issues):
        df_issues = df_issues.groupby("author").size().reset_index(name="Issues opened")
        issues_fig = px.bar(
            data_frame=df_issues,
            x="author",
            y="Issues opened",
            template=template_name,
            title="Number of issues opened by Author",
        )

    # Comment statistics
    df_comments = data["comments"]
    if data_ok(df_comments):
        df_comments = (
            df_comments.groupby("author")
            .agg({"body_length": "sum", "created_at": "count"})
            .reset_index()
        )
        df_comments = df_comments.melt(
            id_vars=["author"],
            var_name="Type",
            value_name="Count",
            value_vars=["body_length", "created_at"],
        )

        comments_fig = px.bar(
            data_frame=df_comments,
            x="author",
            y="Count",
            color="Type",
            template=template_name,
            facet_col="Type",
            facet_col_wrap=1,
            title="Comment Stats by Author",
        )
        comments_fig.update_yaxes(matches=None)

    return commits_fig, prs_fig, issues_fig, comments_fig


clientside_callback(
    """
    switchOn => {       
       document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');  
       return window.dash_clientside.no_update
    }
    """,
    Output("switch", "id"),
    Input("switch", "value"),
)


@dash_app.callback(
    Output("commits-graph", "figure", allow_duplicate=True),
    Output("prs-graph", "figure", allow_duplicate=True),
    Output("issues-graph", "figure", allow_duplicate=True),
    Output("comments-graph", "figure", allow_duplicate=True),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("switch", "value"),
    prevent_initial_call=True,
)
def update_template(theme, color_mode_switch_on):
    theme_name = template_from_url(theme)
    template_name = theme_name if color_mode_switch_on else theme_name + "_dark"

    patched_figure = Patch()
    # When using Patch() to update the figure template, use the figure template dict
    # from plotly.io  and not just the template name
    patched_figure["layout"]["template"] = pio.templates[template_name]
    return patched_figure, patched_figure, patched_figure, patched_figure


@typer_app.command(name="dash")
def run(
    repo: str = typer.Argument(
        ..., help="Repository source in format: 'owner/repository'"
    ),
    csv_file: str = typer.Option(
        "db", help="Filename used to store data downloaded from GitHub :octopus:"
    ),
    interval: int = typer.Option(
        120, help="Time between calls to GitHub, defines how often database is updated."
    ),
    start_date: str = typer.Argument(..., help="Start date in the format YYYY-MM-DD"),
    end_date: str = typer.Argument(..., help="End date in the format YYYY-MM-DD"),
):
    """Monitor a GitHub repository and update commit data to a CSV file at regular
    intervals."""
    global REPO, CSV_FILE, START_DATE, END_DATE, INTERVAL
    REPO = repo
    CSV_FILE = csv_file
    START_DATE = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    END_DATE = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    INTERVAL = interval

    run_app()


if __name__ == "__main__":
    typer_app()
