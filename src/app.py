import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css'], use_pages=True)

app.layout = dbc.Container([
    dbc.NavbarSimple([
        dbc.NavItem(dbc.NavLink(page['name'], href=page['path']))
        for page in dash.page_registry.values()
    ]),
    
    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)