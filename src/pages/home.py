import dash
from dash import Dash, html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_bio
import base64

from components.protein_inputs import sequence_input

dash.register_page(__name__, path='/')

layout = html.Div([
            # Description, center formatted. Text is in italics
            html.H1('Protein Server', style={'textAlign': 'center'}),
            html.P('This server hosts modern protein ML tools.', style={'textAlign': 'center', 'font-style': 'italic'}),

            # File input area for a protein sequence or fasta file.
            sequence_input,
            
            # Sequence Viewer
            dash_bio.SequenceViewer(
                id='sequence-viewer',
            ),            


            # Structure Viewer
            dash_bio.Molecule3dViewer(
                id='structure-viewer',
            ),
        ], 
        style={
            'width': '100%',
            'margin': 'auto',
            'textAlign': 'center',

        }
    )

@callback(
    [Output('sequence-viewer', 'sequence'), Output('structure-viewer', 'modelData')],
    Input('submit-button', 'n_clicks'),
    [State('sequence-upload', 'contents'), State('structure-upload', 'contents'), State('model', 'value')]
)
def update_outputs(n_clicks, sequence, structure, model):
    if n_clicks > 0:
        sequence = base64.b64decode(sequence)
        structure = base64.b64decode(structure)
        return '-', None
    else:
        return '-', None