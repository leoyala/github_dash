import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html
from dash_bootstrap_templates import ThemeChangerAIO


def set_layout(app, interval: int):
    interval = html.Div(
        [
            dcc.Interval(
                id="interval-component",
                interval=interval * 1000,  # in milliseconds
                n_intervals=0,
            )
        ]
    )

    epiloge_span = html.Span(
        [
            "Made with ",
            html.I(className="fa fa-heart", style={"color": "red", "margin": "0 5px"}),
            " by ",
            html.A(
                "Leonardo Ayala.", href="https://github.com/leoyala", target="_blank"
            ),
        ],
        className="d-inline-block ms-1",
    )

    epilogue = html.Div(
        [
            epiloge_span,
        ],
        className="hstack gap-3 mt-2",
    )

    color_mode_switch = html.Span(
        [
            dbc.Label(className="fa fa-moon", html_for="switch"),
            dbc.Switch(
                id="switch",
                value=True,
                className="d-inline-block ms-1",
                persistence=True,
            ),
            dbc.Label(className="fa fa-sun", html_for="switch"),
        ]
    )

    theme_controls = html.Div(
        [
            ThemeChangerAIO(aio_id="theme", radio_props={"value": dbc.themes.SKETCHY}),
            color_mode_switch,
        ],
        className="hstack gap-3 mt-2",
    )

    header = html.H4(
        "GitHub Repository Stats",
        className="bg-primary text-white p-2 mb-2 text-center",
    )

    spinner = html.Div(
        [
            dbc.Spinner(html.Div(id="spinner"), color="success"),
        ]
    )

    app_info = dbc.Alert(
        [
            html.Span(
                [
                    html.I(className="fa fa-info-circle"),
                    "This application uses the ",
                    html.A(
                        "GitHub REST PAI. ",
                        target="_blank",
                        href="https://docs.github.com/en/rest",
                    ),
                    "Be careful not to surpase the ",
                    html.A(
                        "rate limits.",
                        target="_blank",
                        href="https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api",
                    ),
                    "The rate limits can be surpased by reloading the page or restarting the application too often.",
                ]
            )
        ],
        color="info",
        className="d-flex align-items-center",
    )

    controls = dbc.Card(
        [app_info, spinner],
        body=True,
    )

    tab1 = dbc.Tab(
        [dcc.Graph(id="commits-graph", figure=px.bar(template="bootstrap"))],
        label="Commits",
    )
    tab2 = dbc.Tab(
        [dcc.Graph(id="prs-graph", figure=px.bar(template="bootstrap"))], label="PRs"
    )
    tab3 = dbc.Tab(
        [dcc.Graph(id="issues-graph", figure=px.bar(template="bootstrap"))],
        label="Issues",
    )
    tab4 = dbc.Tab(
        [dcc.Graph(id="comments-graph", figure=px.bar(template="bootstrap"))],
        label="Comments",
    )
    tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3, tab4]))

    app.layout = dbc.Container(
        [
            interval,
            header,
            dbc.Row(
                [
                    dbc.Col([theme_controls, controls], width=4),
                    dbc.Col([tabs], width=8),
                ]
            ),
            dbc.Row([dbc.Col([epilogue], width=4)]),
        ],
        fluid=True,
        className="dbc",
    )
