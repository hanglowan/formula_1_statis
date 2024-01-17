import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px

from ff1.ff1 import Session_f1 as Session

dash.register_page(__name__, path='/')

session = Session()
session.set_driver('VER')
year = 2023

layout = \
    html.Div([
        html.Div(
            year,
            id='vars',
            style={'display':'none'}
        ),
        html.Div([
            html.H1("Home")
        ],
            className='div-header'
        ),

        html.Hr(),

        html.Div(
            [
                html.H3(
                    f"{year} Standings",
                    className='div-container'
                ),
                html.Hr()
            ],
            className='div-container'
        ),
        html.Div(
            id='driver-standings',
            className='table table-hover table-active',# div-container div-subcontainer',
            style={
                'padding': '0px 100px 0px 100px',
            }
        ),
        ]
    )

@callback(
    Output('driver-standings', 'children'),
    Input('vars', 'children')
)
def get_driver_standings(vars):
    results = session.driver.f1.get_results(year)

    col_titles = html.Thead(
        html.Tr([
            html.Th('Points', scope='col'),
            html.Th('Driver', scope='col'),
            html.Th('Code', scope='col'),
            html.Th('Wins', scope='col'),
        ],
        )
    )

    col_body = []

    for row in results.itertuples():
        position = row[1]
        points = row[2]
        raceId = row[3]
        wins = row[4]
        number = row[5]
        driverId = row[6]
        driverRef = row[7]
        code = row[8]
        forename = row[9]
        surname = row[10]
        url = row[11]

        link = dash.page_registry['pages.driver_information']['relative_path']

        if code in ['VER', 'BOT', 'SAI', 'LEC', 'GAS', 'VET', 'HAM']:
            name = html.A(
                        f"{forename} {surname}",
                        href=f"{link[:-4]}{code}"
                    )
        else:
            name = f"{forename} {surname}"
        col_body.append(
            html.Tr([
                html.Th(points, scope="row"),
                html.Td(
                    name
                ),
                html.Td(f"{code}"),
                html.Td(f"{wins}"),
            ],
                className="table-secondary"
            ),
        )

    return html.Table([col_titles, html.Tbody(col_body)], className="table table-hover")