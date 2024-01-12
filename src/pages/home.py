import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
from dash.exceptions import PreventUpdate

from f1 import driver_data, formula_1_data
import pandas as pd
import plotly.express as px

drivers = driver_data.Drivers()
form_1 = formula_1_data.Formula_1()


dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div([
        html.H1("Home page: Driver records"),
    ], className='page-header'),

    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Driver Data")
                ], className='col-lg-12'),
                html.Div([
                    html.Div([
                        dash_table.DataTable(data=drivers.get_drivers().to_dict('records'),
                                             page_size=20,
                                             sort_action='native',
                                             style_cell={'textAlign': 'left'},
                                             style_as_list_view=True,
                                             id='driver_info'),
                    ], className='table-info'),
                ], className='bs-component'),
            ], className='row'),
        ], className='bs-docs-section'),
        dcc.Graph(id='graph_drivers'),
        html.P("Year Range:"),
        dcc.RangeSlider(1950, 2023, 1, value=[2019, 2023], id="range_slider_years",
                        marks=dict([(x, f"'{str(x)[2:]}") for x in range(1950, 2024, 5)])),
    ],
        className='bs-docs-section')
], className='container')


@callback(
    Output("graph_drivers", "figure"),
    Input("range_slider_years", "value"))
def display_color(value):
    latest_drivers = form_1.get_year_driver_info(value)
    fig = px.histogram(latest_drivers, x='age', nbins=15)
    return fig
