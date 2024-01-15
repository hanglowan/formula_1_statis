import logging
import math
import pandas as pd
from pathlib import Path
import dash
from dash import html, Input, Output, callback, State, dcc, dash_table, clientside_callback, ctx
from dash.exceptions import PreventUpdate
from driver.driver import Driver
from ff1.ff1 import Session_f1 as Session

logger = logging.getLogger(Path(__file__).name)

position_text = {
    "D": 'Disqualified',
    "E": 'excluded',
    "F": 'Failed to Qualify',
    "N": 'Not Classified',
    "R": 'Retired',
    "W": 'Withdrew',
    "-": '-',
}

dates = [x for x in range(2018, 2024)]

dash.register_page(__name__, path_template='/driver_information/<driver_id>')

session = Session()


def layout(driver_id: str):
    global session
    # backend setup
    session.set_driver(driver_id)
    latest_year = session.driver.get_last_year()
    latest_circuit = session.driver.get_last_circuit()
    logger.info("start: SETTING SESSION: %s, %s", latest_year, latest_circuit)
    session.set_session(latest_year, latest_circuit, 'R')

    session.print_vars()

    driver_info = session.get_driver()

    driver = session.driver
    all_info = driver.all_info()
    logger.info("all info: %s", all_info)

    layout = html.Div([
        html.Div([
            dcc.Location(id='url'),
            html.Div(id='viewport-container')
        ]),
        html.Div(
            id='circuit-variables',
            style={"display":"none"}
        ),
        # html.Div(
        #     f"You selected: {driver_id}, year {latest_year}",
        #     className='div-container h6'
        # ),
        html.Div(
            html.H1("Driver information"),
            className='bs-component div-header'
        ),
        # html.Div(
        #     id='bug-output'
        # ),

        html.Hr(),

        html.Div([
            html.Div([
                html.Div(
                    id='race-title',
                    className='div-container'
                ),
                html.Div(
                    id='results-summary-title',
                    className='div-container',
                    style={
                        'font_size': '12px'
                    }
                ),

                html.Hr(className='div-container'),

                html.Div([
                    html.Div(
                        dcc.Dropdown(
                            clearable=False,
                            id='comparison-dropdown-lap',
                        ),
                        className='col-md-3 h6'
                    ),
                    html.Div(
                        dcc.Dropdown(
                            options=['Speed', 'Brake', 'Throttle', 'nGear', 'RPM'],
                            value='Speed',
                            clearable=False,
                            id='comparison-dropdown-measure',
                        ),
                        className='col-md-3 h6'
                    ),
                ],
                    className='row div-container'
                ),
                #
                # html.Hr(className='div-container'),
                #
                # html.Div(
                #     'circuit-checklist',
                #     id='circuit-checklist',
                #     className='div-container'
                # ),
                html.Div(
                    html.Div([
                        dcc.Graph(
                            id='circuit-display',
                            # # className='div-para',
                            # style={
                            #     'outline-style': 'solid',
                            #     'outline-color': 'red',
                            #     'outline-width': '0.5rem'
                            # }
                        ),
                        html.Button(
                            'show legend',
                            className='h6 btn btn-dark',
                            id='show-legend',
                            n_clicks=0,
                            style={'position': 'absolute',
                                   'left': '2rem',
                                   'width': '4rem',
                                   'line-height': '0.75rem',
                                   'padding-top': '0.25rem',
                                   'padding-bottom': '.25rem',
                                   'padding-left': '0.5rem',
                                   'padding-right': '0.5rem',
                                   'height': '2rem',
                                   'font-size': '.5rem',
                                   'top': '1.25rem'}
                        ),
                    ],
                        className='row',
                        style={'position': 'relative'}
                    ),
                )
            ],
                className='col-md-9 div-para'
            ),
            html.Div([
                html.Div([
                    html.Div(
                        id='driver-image'
                    ),
                    html.Div([
                        html.Span(
                            f"#{driver_info['DriverNumber']}",
                            className='h3'
                        ),
                    ],
                        className='div-para'
                    ),
                    html.Span(
                        f"{driver_info['FirstName']} {driver_info['LastName']} ",
                        className='h4',
                    ),
                    html.Span(
                        driver_id,
                        className='h6',
                        id='driver-id-start'
                    ),
                    html.Div(
                        id='constructor-info'
                    ),
                ],
                    id='driver-title',
                    className='div-title'
                ),

                html.Hr(),

                html.Div(
                    id='last-race-info'
                ),

                html.Hr(),

                html.Div(
                    id='driver-basic-info'
                ),

                html.Hr(),

                html.Div(
                    id='latest-year-records'
                ),

                html.Hr(),

                html.Div([
                    dcc.Dropdown(
                        options=list(set(session.driver.years_participated()) & set(dates)),
                        placeholder='Select Season',
                        value=latest_year,
                        id='dropdown-seasons',
                        persistence=True,
                        className='h6'
                    ),
                    dcc.Dropdown(
                        # optionHeight=70,
                        id='dropdown-season-circuits',
                        persistence=True
                    ),
                ],
                    className='div-para h6'
                ),
            ],
                className='col-md-3 div-para'
            ),
        ],
            className='row div-container'
        ),

        html.Hr(),

        html.Div([
            html.Div(
                html.H1('Statistics'),
                id='stats-title',
                className='col-lg-12 div-container'
            ),

            html.Hr(),

            html.Div([
                html.Div([
                    html.Div([
                        html.H6("X-Axis:"),
                        dcc.RadioItems(
                            options=[' time', ' distance'],
                            value=' time',
                            id='x-axis-select'
                        ),
                    ],
                        className='div-para h6'
                    ),

                    html.Hr(),

                    html.Div([
                        html.H6("Laps:"),
                        dcc.Dropdown(
                            multi=True,
                            placeholder='select laps to compare',
                            clearable=True,
                            id='compare-lap-dropdown'
                        )],
                        className='div-para h6'
                    ),

                    html.Hr(),

                    html.Div([
                        html.H6("METRICS:"),
                        dcc.Dropdown(
                            options=['speed', 'throttle', 'gear', 'rpm', 'brakes'],
                            value='speed',
                            multi=True,
                            placeholder='select metrics to compare',
                            clearable=False,
                            id='compare-metric-dropdown'
                        )],
                        className='div-para h6'
                    )
                ],
                    className='col-md-2 h6',
                ),
                html.Div([
                    dcc.Graph(id='basic-stats-display')
                ],
                    className='col-md-10',
                )],
                className='row'
            ),

        ],
            className='row div-container'
        ),
        html.Hr(),
        html.Div(
            id='basic-info-title',
            className='bs-component div-margin'
        ),
        html.Hr(className='bs-component div-margin'),
        html.Div(
            id='basic-stats-info',
            className='bs-component div-margin'
        ),
        html.Div([
            html.Div([
                dash_table.DataTable(id='qualifying-table',
                                     page_size=15,
                                     sort_action='native',
                                     style_cell={'textAlign': 'left'},
                                     style_as_list_view=True,
                                     ),
            ])
        ], className='bs-component div-margin'),
    ])

    return layout


clientside_callback(
    """
    function(href) {
        var w = window.innerWidth;
        var h = window.innerHeight;
        return {'height': h, 'width': w};
    }
    """,
    Output('viewport-container', 'children'),
    Input('url', 'href')
)


@callback(
    Output('basic-stats-display', 'figure'),
    Input("circuit-variables", 'children'),
    Input("compare-lap-dropdown", 'value'),
    Input('x-axis-select', 'value'),
    Input('viewport-container', 'children'),
    Input('compare-metric-dropdown', 'value')
)
def get_basic_stats_display(vars, lap_numbers, x_axis, dims, metrics):
    logger.info("CALL BASIC STATS: %s, %s, %s", lap_numbers, x_axis, metrics)

    fig = session.get_basic_stats_display(lap_numbers, metrics, dims['width'], x_axis)

    return fig


@callback(
    Output('compare-lap-dropdown', 'options'),
    # Output('compare-lap-dropdown', 'value'),
    Input('circuit-variables', 'children'),
    # Input('x-axis-select', 'value'),
)
def get_compare_lap_dropdown(vars):
    laps = session.laps_participated()

    dropdown = []
    for lap in laps:
        dropdown.append({'label': f"{int(lap)}",
                         'value': lap})

    return dropdown  # , dropdown[0]['value']


@callback(
    Output("circuit-variables", 'children'),
    Input("dropdown-seasons", "value"),
    Input("dropdown-season-circuits", "value"),
)
def load_new_session(season, circuit_id):
    div = f"{season}-{circuit_id}"

    logger.info("CALLBACK UPDATE SESSION: %s", div)

    circuit_name = session.driver.f1.get_circuit_name(season, circuit_id)
    logger.info("CIRCUIT NAME: %s", circuit_name)

    session.set_session(season, circuit_name, 'R')

    return div


@callback(
    Output('comparison-dropdown-lap', 'options'),
    Output('comparison-dropdown-lap', 'value'),
    Input('circuit-variables', 'children')
)
def get_comparison_dropdown_1(vars):
    dropdown = []
    for lap in session.laps_participated():
        dropdown.append({'label': f'lap {int(lap)}',
                         'value': int(lap)})

    return dropdown, dropdown[0]['value']


@callback(
    Output("circuit-display", 'figure'),
    Input("circuit-variables", "children"),
    Input('viewport-container', 'children'),
    Input('show-legend', 'n_clicks'),
    Input('comparison-dropdown-lap', 'value'),
    Input('comparison-dropdown-measure', 'value')
)
def get_circuit_display(vars, dimensions, legend_toggle, lap, measure):

    logger.info("screen dimensions: %s", dimensions)
    fig = session.get_circuit_fig(screen_height=dimensions['height'],
                                  screen_width=dimensions['width'],
                                  show_legend=(legend_toggle%2 == 1),
                                  measure=measure,
                                  lap=lap)
    # print(fig)

    return fig


@callback(
    Output("bug-output", "children"),
    # State("dropdown-seasons", "value"),
    Input("circuit-variables", "children"),
)
def bug_output(vars):
    vars = vars.split("-")
    season = int(vars[0])
    circuit_id = int(vars[1])

    # circuit_df = session.driver.ergast.get_circuits(season=season)
    circuit_name = session.driver.f1.get_circuit_name(season, circuit_id)
    div = [
        html.Div(
            f"season: {season}",
        ),
        html.Div(
            f"circuit_id: {circuit_id}",
        ),
        html.Div(
            f"circuit_name: {circuit_name}"
        ),
    ]

    return div

@callback(
    Output('driver-image', 'children'),
    Input("circuit-variables", "children"),
    Input('viewport-container', 'children')
)
def get_driver_image(vars, dim):
    vars = vars.split("-")
    season = int(vars[0])
    circuit_id = int(vars[1])
    width =dim['width']/4
    lastname = session.get_driver()['LastName'].lower()

    link = f"https://media.formula1.com/content/dam/fom-website/drivers/{season}Drivers/{lastname}.jpg"
    logger.info("%s: driver image link: %s", lastname, link)
    div = [
        html.Div([
            html.Img(
                # src=driver_info['HeadshotUrl']
                src=link,
                # src="https://media.formula1.com/content/dam/fom-website/manual/Helmets2023/albon.png",
                height=width*6/7,
            ),
        ],
            className='div-para',
            style={
                'overflow': 'hidden',
                'height': width*4/7,
                'width': width
            }
        ),
    ]
    return div

@callback(
    Output('results-summary-title', 'children'),
    Input("circuit-variables", "children"),
    State('driver-id-start', 'children')
)
def get_results_summary_title(vars, driver_id):
    vars = vars.split("-")
    season = int(vars[0])
    circuit_id = int(vars[1])

    results = session.session.result_data
    results = results[results.Abbreviation == driver_id]

    x = results.Time.iloc[0]
    time_str = 'NaN'
    if not pd.isnull(x):
        time_str = f"{int(x.seconds / 3600)}:{int(x.seconds / 60)}:{x.seconds % 60}.{str(x.microseconds).zfill(6)}"

    div = [
        html.Div(
            html.Span(
                f"P{results.ClassifiedPosition.iloc[0]} | {int(results.Points.iloc[0])} points | finishing time: {time_str} | {results.Status.iloc[0]}",
                className='h6'
            )
        ),
        html.Div(
            html.Span(
                f"grid position: {int(results.GridPosition.iloc[0])} | Q1: {results.Q1.iloc[0]} | Q2: {results.Q2.iloc[0]} | Q3: {results.Q3.iloc[0]}",
                className='h6'
            )
        )
    ]

    return div


@callback(
    Output('race-title', 'children'),
    Input("circuit-variables", "children"),
    State('driver-id-start', 'children')
)
def get_race_title(vars, driver_id):
    vars = vars.split("-")
    season = int(vars[0])
    circuit_id = int(vars[1])

    logger.info("get_race_title circuit, season: %s, %s", circuit_id, season)

    circuit_name = session.driver.f1.get_circuit_name(season, circuit_id)
    logger.info("circuit_name: %s", circuit_name)

    event_name = session.session.get_event_info('EventName')
    logger.info("eventname: %s", event_name)

    try:
        total_laps = session.session.get_total_laps()
    except:
        total_laps = "-"
        logger.error("SESSION NOT LOADED")

    div = [
        html.Div([
            html.Span(
                f"{event_name} ",
                className='h1'
            ),
            html.Span(
                f"{session.session.get_event_info('Location')} | Circuit {session.session.get_event_info('RoundNumber')}",
                className='h6'
            ),
        ]),
        html.Div([
            html.Span(
                f"{str(session.session.get_event_info('EventDate').month).zfill(2)}-{str(session.session.get_event_info('EventDate').day).zfill(2)}-{session.session.get_event_info('EventDate').year} | Total Laps: {total_laps}",
                className='h6'
            )
        ]),

        html.Hr(),

        html.Div([
            html.Span(
                f"{session.session.get_driver_info(driver_id, 'DriverNumber')} {session.session.get_driver_info(driver_id, 'FullName')} ",
                className='h4'
            ),
            html.Span(
                f"{session.session.get_driver_info(driver_id, 'TeamName')}",
                className='h6'
            )
        ], className='div-para'),
    ]

    return div


@callback(
    Output('dropdown-season-circuits', 'options'),
    Output('dropdown-season-circuits', 'value'),
    Input('dropdown-seasons', 'value')
)
def get_dropdown_season_circuits(season):
    circuit_names, circuit_ids = session.driver.get_circuit_names_ids(season)

    dropdown = []
    for index, name in enumerate(circuit_names):
        # print(name)
        if season==2018 and name in ['Australian Grand Prix', 'Bahrain Grand Prix']:
            continue
        dropdown.append({'label': name,
                         'value': circuit_ids[index]})

    logger.info("dropdown: %s", dropdown)

    return dropdown, dropdown[0]['value']


@callback(
    Output('latest-year-records', 'children'),
    Input('driver-id-start', 'children')
)
def get_latest_year_records(driver_id):
    latest_year = session.driver.get_last_year()
    # latest_circuit = session.driver.get_last_circuit()
    df = session.driver.get_final_results(latest_year, driver_id)

    div = [
        html.Span(
            f"{latest_year} standings: P{df['position'].iloc[0]} | {df['points'].iloc[0]} Points",
            className='h6'
        )
    ]

    return div


@callback(
    Output('driver-basic-info', 'children'),
    Input('driver-id-start', 'children')
)
def get_driver_basic_info(driver_id):
    all_info = session.driver.all_info()
    div = [
        html.Div(
            f"Nationality: {all_info['nationality']}",
            className='h6'
        ),
        html.Div(
            f"Date of Birth: {all_info['dob']}",
            className='h6'
        )
    ]

    return div


@callback(
    Output('constructor-info', 'children'),
    Input('driver-id-start', 'children')
)
def get_constructor_info(driver_id):
    results = session.session.result_data
    driver_info = results[results['Abbreviation'] == driver_id]

    div = [
        html.Span(
            f"{driver_info['TeamName'].iloc[0]}",
            className='h6',
        ),
    ]

    return div


@callback(
    Output('last-race-info', 'children'),
    Input('driver-id-start', 'children')
)
def get_last_race_info(driver_id):
    results = session.session.result_data
    driver_info = results[results['Abbreviation'] == driver_id]

    div = [
        html.H6(
            f"Last Race: {session.session.get_event_info('EventName')}"
        ),
        html.Span(
            f"P{driver_info['ClassifiedPosition'].iloc[0]} | Points: {driver_info['Points'].iloc[0]} | {driver_info['Status'].iloc[0]}",
            className='h6',
        ),
    ]

    return div


@callback(
    Output('basic-stats-info', 'children'),
    Input('dropdown-circuit-id-selected', 'value'),
    Input("dropdown-driver-id-selected", "value"),
    Input("dropdown-season-selected", 'value')
)
def get_stats_info(cId, dId, yr):
    if not cId:
        raise PreventUpdate

    driver = Driver(dId)
    qualify_info = driver.qualify_info(yr, cId)
    div = [
        html.H4("Statistics: Summary"),
        html.Div([
            html.H5("Qualifying:"),
            html.H6(
                "Grid Position: " + str(qualify_info['position'])
            ),
            html.P("Q1: " + qualify_info['q1'] +
                   " | Q2: " + qualify_info['q2'] +
                   " | Q3: " + qualify_info['q3'])
        ]),
    ]

    return div


@callback(
    Output('qualifying-table', 'data'),
    Input('dropdown-circuit-id-selected', 'value'),
    Input("dropdown-driver-id-selected", "value"),
    Input("dropdown-season-selected", 'value')
)
def get_lap_times(cId, dId, szn):
    if not cId:
        raise PreventUpdate
    return Driver(dId).lap_info(szn, cId).to_dict('records')
