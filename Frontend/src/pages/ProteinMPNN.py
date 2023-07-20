import dash
from dash import Dash, html, dcc
dash.register_page(__name__, 
                   path='/ProteinMPNN',
                   name='ProteinMPNN',
                   title='ProteinMPNN Dashboard',
                   )

def layout():
    return html.Div([
        
    ])
