import dash
import dash_bootstrap_components as dbc
from dash import Dash, html
import fastf1 as fastf1
import logging
from pathlib import Path

logging.basicConfig(format='%(asctime)s [%(name)s:%(lineno)d:%(funcName)s] [%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(Path(__file__).name)

# Initialize app
app = Dash(__name__, use_pages=True,
           suppress_callback_exceptions=True,
           assets_folder=str(Path(Path(__file__).parent, 'assets')),
           external_stylesheets=[dbc.themes.LUX])

def driver_ids():
    link = dash.page_registry['pages.driver_information']['relative_path']
    drivers = fastf1._DRIVER_TEAM_MAPPING
    children = []
    for numid in drivers:
        if drivers[numid]['Abbreviation'] in ['VER', 'BOT', 'SAI', 'LEC', 'GAS', 'VET', 'HAM']:
            children.append(
                dbc.DropdownMenuItem(str(drivers[numid]['FirstName'] + " " + drivers[numid]['LastName']),
                                     href=f"{link[:-4]}{drivers[numid]['Abbreviation']}",
                                     # external_link=True,
                                     # className='dropdown-item'
                                     )
            )

    return children


navigation = dbc.NavbarSimple([
    dbc.NavItem(dbc.NavLink(
        "Home",
        href=dash.page_registry['pages.home']['relative_path']),
        className='nav-dropdown',
    ),
    dbc.NavItem(dbc.DropdownMenu(
        children=driver_ids(),
        label='Drivers',
        className='nav-dropdown'),
    )
],
    brand='F1 Statistics',
    className='navbar navbar-expand-lg bg-primary',
    style={
        '--bs-navbar-brand-hover-color': '#cd3838'
    }
)

app.layout = html.Div([
    html.Div([
        navigation,
    ],
        id="navigation_bar",
    ),
    html.Div([
        dash.page_container,
    ])
])


# @app.callback(
#     Output('driver-dropdown', 'children')
# )
# def get_drivers():
#
#     return children


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8654, debug=False)
