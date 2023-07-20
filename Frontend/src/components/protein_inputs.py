from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

# Make a sequence input
# Users can either upload a txt or fasta file, or provide a protein sequence in the textarea

inactive_style = {
    'width': '100%',
    'height': '60px',
    'lineHeight': '60px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'textAlign': 'center',
    'display': 'none'
}

active_style = {
    'width': '100%',
    'lineHeight': '60px',
    'borderWidth': '2px',
    'borderStyle': 'dotted',
    'borderRadius': '5px',
    'borderColor': 'blue',
    'textAlign': 'center',
    'verticalAlign': 'middle'
}

sequence_input = html.Div([
    dbc.Row(
        [
            dbc.Col(
                [
                    dcc.Upload(
                        id='sequence-upload',
                        children=[],
                        multiple=False, 
                        accept='.fasta',
                        style={
                            'width': '100%',
                            'height': '100px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center'
                        }
                    ),                
                    dcc.Upload(
                        id='structure-upload',
                        children=[],
                        multiple=False, 
                        accept='.pdb',
                        style={
                            'width': '100%',
                            'height': '100px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center'
                        }
                    ),
                ],
            ),
            dbc.Col(
                [
                    html.P('Language Model'),
                    dcc.RadioItems(
                        options=[
                            {'label': 'ESM-1v', 'value': 'ESM-1v', 'disabled': True}, 
                            {'label': 'ESM-2', 'value': 'ESM-2'}, 
                            {'label': 'ProGEN2', 'value': 'ProGEN2', 'disabled': True}],
                        value='ESM-2',
                        id='model', 
                        inline=False,
                        labelStyle={'display': 'block'},
                        ),
                ],
            )

        ],
        style={
                'width': '100%',
                'lineHeight': '60px',
                'borderWidth': '2px',
                'borderStyle': 'solid',
                'borderRadius': '1px',
                'borderColor': 'black',
                'textAlign': 'center',
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',

        }
    ),

    # Make the textarea the same style as the upload
    dcc.Textarea(
        id='sequence-input',
        placeholder='Protein Sequence (amino acids)',
        style={
            'width': '100%',
            'height': '200px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'display': 'none'
        }
    ),

    # Submit button
    dbc.Button('Submit', id='submit-button', n_clicks=0),

    # Hidden Div State
    html.Div(id='hidden-div-state', style={'display': 'none'})
])

@callback(
    Output('sequence-upload', 'children'),
    Input('sequence-upload', 'contents'),
    State('sequence-upload', 'filename')
)
def update_label(contents, filename):
    if contents:
        return [f'{filename} or ',
                html.A(html.B('Select a File'))]
    else:
        return ['Drop a FASTA file or ',
                html.A(html.B('Select a FASTA file'))]


@callback(
    Output('structure-upload', 'children'),
    Input('structure-upload', 'contents'),
    State('structure-upload', 'filename')
)
def update_label(contents, filename):
    if contents:
        return [f'{filename} or ',
                html.A(html.B('Select a File'))]
    else:
        return ['Drop the accompanying PDB file (will use ESMFold otherwise) or ',
                html.A(html.B('Select the file'))]