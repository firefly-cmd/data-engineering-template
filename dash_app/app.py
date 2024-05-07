import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import sqlalchemy
from dash_bootstrap_templates import load_figure_template

# Load the dark theme for the entire app
load_figure_template("DARKLY")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div(
    [
        dbc.NavbarSimple(
            brand="Real-time Application Analysis",
            brand_href="#",
            color="dark",
            dark=True,
        ),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(dcc.Graph(id="app-1-gauge"), width=4),
                        dbc.Col(dcc.Graph(id="app-2-gauge"), width=4),
                        dbc.Col(dcc.Graph(id="app-3-gauge"), width=4),
                    ],
                    align="center",
                ),
                dbc.Row([dbc.Col(dcc.Graph(id="error-trends"), width=12)]),
                dbc.Row(
                    [
                        dbc.Col(dcc.Graph(id="latency-metrics"), width=6),
                        dbc.Col(dcc.Graph(id="request-distribution"), width=6),
                    ]
                ),
                dcc.Interval(
                    id="interval-component", interval=10 * 1000, n_intervals=0
                ),
            ],
            fluid=True,
        ),
    ]
)


@app.callback(
    [
        Output("app-1-gauge", "figure"),
        Output("app-2-gauge", "figure"),
        Output("app-3-gauge", "figure"),
        Output("error-trends", "figure"),
        Output("latency-metrics", "figure"),
        Output("request-distribution", "figure"),
    ],
    Input("interval-component", "n_intervals"),
)
def update_metrics(n):
    # Create database connection
    engine = sqlalchemy.create_engine("postgresql://admin:admin@postgres:5432/logs")

    # Using context managers for handling database connections
    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT * FROM application_metrics ORDER BY enddate DESC LIMIT 3", conn
        )

        error_data = pd.read_sql(
            """
            SELECT application_id, enddate, error_rate
            FROM application_metrics
            ORDER BY application_id, enddate
            LIMIT 300;
            """,
            conn,
        )

    # Create gauges for the latest error rates as percentages
    gauges = []
    for i in range(1, 4):
        app_data = df[df["application_id"] == f"app_{i}"]
        error_rate = app_data["error_rate"].values[0] if not app_data.empty else 0
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=error_rate,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": f"App {i} Error Rate", "align": "center"},
                gauge={"axis": {"range": [None, 100]}},
            )
        )
        gauge.update_layout(template="plotly_dark")
        gauges.append(gauge)

    # Error Trends Plot
    error_trends = go.Figure()
    for app_id in error_data["application_id"].unique():
        app_data = error_data[error_data["application_id"] == app_id]
        error_trends.add_trace(
            go.Scatter(
                x=app_data["enddate"],
                y=app_data["error_rate"],
                mode="lines+markers",
                name=f"App {app_id}",
            )
        )

    error_trends.update_layout(
        title="Error Rate Trends Over Time",
        xaxis_title="Time",
        yaxis_title="Error Rate (%)",
        legend_title="Application ID",
        template="plotly_dark",
    )

    # Latency Metrics Plot
    latency_metrics = go.Figure(
        go.Bar(
            x=df["application_id"],
            y=df["average_latency"],
            text=df["average_latency"],
            textposition="auto",
        )
    )
    latency_metrics.update_layout(
        title="Average Latency per Application",
        xaxis_title="Application ID",
        yaxis_title="Latency (ms)",
        template="plotly_dark",
    )

    # Request Distribution Plot
    request_distribution = go.Figure()
    request_types = ["get_requests", "post_requests", "put_requests", "delete_requests"]
    for request_type in request_types:
        request_distribution.add_trace(
            go.Bar(
                x=df["application_id"],
                y=df[request_type],
                name=request_type.split("_")[0].upper(),
            )
        )

    request_distribution.update_layout(
        barmode="group",
        title="Request Distribution per Application",
        xaxis_title="Application ID",
        yaxis_title="Number of Requests",
        template="plotly_dark",
    )

    return gauges + [error_trends, latency_metrics, request_distribution]


if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0")
