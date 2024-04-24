#!/usr/bin/env python3.8

# Copyright [2020] EMBL-European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import dash
from dash import dash_table
from dash import html
from dash import dcc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import datetime
from dash.exceptions import PreventUpdate
import argparse, hashlib, os, subprocess, sys, time
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
load_figure_template('minty')



parser = argparse.ArgumentParser(prog='dashboard.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |  European Nucleotide Archive (ENA) data flow monitoring Dashboard  |
        |                                                              |
        |                 |
        + =========================================================== +      
        """)
parser.add_argument('-f', '--file', help='Analysis and Sequence directory', type=str, required=True)
args = parser.parse_args()

def uploading_dataframes():
    read_df = pd.read_csv(f'{args.file}/API.reads.output.recent.csv', sep=",").dropna()
    seq_df = pd.read_csv(f'{args.file}/API.sequence.output.recent.csv', sep=",").dropna()
    webin_count_merge_final = pd.read_csv(f'{args.file}/SQL-API.reads_webin.log.csv', sep=",")
    project_count_merge_final = pd.read_csv(f'{args.file}/SQL-API.reads_project.log.csv', sep=",")
    webin_seq = pd.read_csv(f'{args.file}/SQL-API.sequence_webin.log.csv', sep=",")
    project_seq = pd.read_csv(f'{args.file}/SQL-API.sequence_project.log.csv', sep=",")
    INSDC_seq = pd.read_csv(f'{args.file}/API.INSDC_seq.output.recent.csv', sep=",")
    center_names = pd.read_csv(f'{args.file}/SQL-API.reads_center_names.log.csv', sep=",")
    center_names_seq = pd.read_csv(f'{args.file}/SQL-API.sequence_center_names.log.csv', sep=",")

    return read_df, seq_df , webin_count_merge_final, project_count_merge_final,webin_seq,project_seq,INSDC_seq, center_names, center_names_seq

def webin_notes():
    webin_notes = pd.read_csv(f'{args.file}/webin_notes.csv')
    webin_seq_notes = pd.read_csv(f'{args.file}/webin_seq_notes.csv')
    return webin_notes, webin_seq_notes

def project_notes():
    project_notes = pd.read_csv(f'{args.file}/project_notes.csv')
    project_seq_notes = pd.read_csv(f'{args.file}/project_seq_notes.csv')

    return project_notes, project_seq_notes

def formatting_notes_tickets(df,column_name):
    for i, value in df[column_name].iteritems():
        if value == None:
            df.at[i, column_name] = ''
    return df

def formatting_x_y(df,column_x, column_y ):
    df_mod = df.where(pd.notnull(df), None)
    for x, value_x in df_mod[column_x].iteritems():
        for y, value_y in df_mod[column_y].iteritems():
            if value_x != [None, np.nan, 'NaN'] and value_y != None:
                if x == y:
                    df_mod.at[x, column_x] = np.nan

            elif value_x != None and value_y == '':
                if x == y:
                    df_mod.at[x, column_x] = np.nan
    return df_mod


###################################
#                                 #
#             MAIN                #
####################################

#Uploading Dataframes
upload_df = uploading_dataframes()
read_df = upload_df[0]
seq_df = upload_df[1]
webin_count_merge_final = upload_df[2]
project_count_merge_final = upload_df[3]
webin_seq = upload_df[4]
project_seq = upload_df[5]
INSDC_df =upload_df[6]
INSDC_seq = INSDC_df.drop('Submission Date', axis=1).groupby(by='country')['Submissions'].sum().reset_index(name='Submissions')
print(INSDC_seq)
center_names = upload_df[7] #.drop(columns='Centers Counts')
center_names_seq = upload_df[8] #.drop(columns='Centers Counts')



#Upload the notes and tickets table
webin_note_df = webin_notes()
webin_notes = webin_note_df[0]
project_note_df = project_notes()
project_notes = project_note_df[0]
webin_seq_notes = webin_note_df[1]
project_seq_notes = project_note_df[1]

# Merge the stat tables with notes table
webin_count_merge = pd.merge(webin_count_merge_final,webin_notes, on=['Webin Account', 'Country'], how='outer')
project_count_merge =pd.merge(project_count_merge_final,project_notes, on=['Webin Account','Project ID', 'Country'], how='outer')
webin_seq_merge = pd.merge(webin_seq,webin_seq_notes, on=['Webin Account', 'Country'], how='outer')
project_seq_merge =pd.merge(project_seq,project_seq_notes, on=['Webin Account','Project ID', 'Country'], how='outer')

#Join Tables ( sequences with Reads)
country_inner_join = pd.merge(seq_df, read_df, on='country', how='outer')
country_inner_join1 = country_inner_join.where(pd.notnull(country_inner_join), 0)
country_inner_join_mod=country_inner_join1.rename(columns={'Submission Date_x': 'Sequences Submission Date','Submissions_x': 'Sequences Submissions','Submission Date_y': 'Reads Submission Date','Submissions_y': 'Reads Submissions'})



#######################
#                      #
#     DASHBOARD        #
########################

def dashboard ():
    image_path = 'assets/ENA_logo_2021.png'
    row = dbc.Container([html.Div([
        dbc.Row([
        dbc.Col(html.Img(src=image_path, style={'height':'100%', 'width':'100%'}), width={"size": 2, "offset": 1}, sm=4, md=3, lg=2),

        dbc.Col(
        html.Div([
        html.H1('SARS-CoV-2 Country Submission Tracking Dashboard'),
        #html.P(['This Dashboard shows Country submission.',html.Br()])
        ]),
            width={"size": 8, "offset": 0}, sm=7, align="center")]), #, align="end"]

        dbc.Row([
            dbc.Col(html.Div([

        dcc.Dropdown(id='country-dropdown', options=[{'label': i, 'value': i} for i in country_inner_join_mod['country'].unique()] , placeholder="Select a Country", value='USA'),
        dcc.Tabs(id="tabs-with-classes",
        value='tab',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        colors={
                     "border": "white",
                     "primary": "white",
                     "background": "#5f9ea0"
                 },
        children=[
            dcc.Tab(label='Country Graphs', value='tab-1', className='custom-tab',
                selected_className='custom-tab--selected',
                    children=[
            dcc.Graph(id='country-graph'),
            dcc.Graph(id='country-reads_graph'),
            dcc.Interval(
                    id='interval-component',
                    disabled=False,
                    interval=10*60000, # in milliseconds
                    n_intervals=0
                ),
            ]),
            dcc.Tab(label='Country Read Stats', value='tab-2', className='custom-tab',selected_className='custom-tab--selected',
                    children=[html.Br(), dbc.Row([dbc.Col(html.Label("General view for ENA Data  ", style={'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}), width=11), html.Br(),
                                                  dbc.Col(dcc.Clipboard(id="webin_reads_copy", style={"fontSize":20, "display": "inline-block"}), align="end", width=1, className="d-grid gap-2 d-md-flex justify-content-md-end")], justify="end"),
                dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i, "editable": (True if i == 'Notes' or i == 'Related tickets' else False)} for i in webin_count_merge.columns],
                    editable=True,
                data=webin_count_merge.to_dict('records'),
                style_cell={'textAlign': 'center','padding': '10px','font_size': '10px'},
                    style_table={'width': '100%'},
                    style_data={'whiteSpace': 'pre-line', 'lineHeight': '15px'},
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit; line-height: 15px'
                    }],
                style_header={
                    'backgroundColor': 'white'
                },
                style_header_conditional=[
                    {
                        'if': {'column_id': ['Webin Account', 'Country', 'Project','Samples','Runs','Experiments']},
                        'color': 'black',
                        'fontWeight': 'bold',
                        'border': '1px solid black'
                    }
                ],
                style_cell_conditional=[
                    {'if': {'column_id': 'Notes'},
                     'width': '20%'},
                    {'if': {'column_id': 'Related tickets'},
                     'width': '20%'},
                    {
                        'if': {'column_id': ['Webin Account', 'Country', 'Project','Samples','Runs','Experiments']},
                        'border': '1px solid black',
                        'font_size': '14px'
                    }
                ],
                ),
                html.Button(id="webin-save-button", children="Save Notes", n_clicks=0),
                html.Div(id="output-1"),







                    html.Br(), dbc.Row([dbc.Col(html.Div([
                                        html.Label("Detailed view for ENA Data  ", id='webin_reads_label', style={'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}), html.Br(),
                                        html.Label("Choose a Webin id from the dropdown to view its content",id='webin_reads_sublabel', style={'color': 'Black', 'fontWeight': 'bold', 'fontSize': 12})]), width=11),
                                        dbc.Col(dcc.Clipboard(id="project_reads_copy", style={"fontSize":20, "display": "inline-block"}), align="end", width=1, className="d-grid gap-2 d-md-flex justify-content-md-end")], justify="end"),

                dcc.Dropdown(id='webin-dropdown', options=[{'label': i, 'value': i} for i in project_count_merge['Webin Account'].unique()], placeholder="Select a Webin ID", value='Webin'),
                dash_table.DataTable(
                id='webin-table',
                columns=[{"name": i, "id": i, "editable": (True if i == 'Notes' or i == 'Related tickets' else False)} for i in project_count_merge.drop(['Webin Account','Country'], axis=1).columns],
                    editable=True,
                data=project_count_merge.to_dict('records'),
                style_cell={'textAlign': 'center', 'font_size': '10px','padding': '1px'},
                    style_table={'width': '100%'},
                    style_data={'whiteSpace': 'pre-line', 'lineHeight': '15px'},
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit; line-height: 15px'
                    }],
                style_header={
                    'backgroundColor': 'white', 'display': 'none'
                },
                style_header_conditional=[
                    {
                        'if': {'column_id': ['Project ID', 'Samples', 'Experiments']},

                        'color': 'black',
                        'fontWeight': 'bold',
                        'border': '1px solid black'
                    }

                ],
                style_cell_conditional=[
                    {'if': {'column_id': 'Notes'},
                     'width': '20%'},  # 'overflow': 'hidden', 'textOverflow': 'ellipsis', 'maxWidth': 0},
                    {'if': {'column_id': 'Related tickets'},
                     'width': '20%'},
                    {
                        'if': {'column_id': ['Project ID', 'Samples', 'Experiments']},
                        'border': '1px solid black', 'font_size': '12px'
                    }],),
                html.Button(id="project-save-button", children="Save Notes", n_clicks=0),
                html.Div(id="output-2"),# children="Press button to save changes to Notes"),


                html.Br(), dbc.Row([dbc.Col(html.Div([
                                        html.Label("Center Names List  ", id='centerName_reads_label', style={'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}), html.Br(),
                                        html.Label("Choose a Project ID from the dropdown to view the associated center names",id='centerName_reads_sublabel', style={'color': 'Black', 'fontWeight': 'bold', 'fontSize': 12})]), width=11),
                                        dbc.Col(dcc.Clipboard(id="centerName_reads_copy", style={"fontSize":20, "display": "inline-block"}), align="end", width=1, className="d-grid gap-2 d-md-flex justify-content-md-end")], justify="end"),

                dcc.Dropdown(id='centerName-reads-dropdown', options=[{'label': i, 'value': i} for i in
                                                         project_count_merge['Project ID'].unique()], placeholder="Select a Project ID",value='select'),
                dash_table.DataTable(
                  id='centerName-reads-table',
                  columns=[
                      {"name": i, "id": i}
                      for i in center_names.drop(['Webin Account', 'Country'], axis=1).columns],
                  data=center_names.to_dict('records'),
                  style_cell={'textAlign': 'center', 'font_size': '10px', 'padding': '1px'},
                    style_table={'width': '100%'},
                    style_data={'whiteSpace': 'pre-line', 'lineHeight': '15px'},
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit; line-height: 15px'
                    }],
                  style_header={
                      'backgroundColor': 'white'
                  },
                  style_header_conditional=[
                      {
                          'if': {'column_id': ['Project ID', 'Samples', 'Experiments']},

                          'color': 'black',
                          'fontWeight': 'bold',
                          'border': '1px solid black'
                      }
                  ],
                  style_cell_conditional=[
                      {
                          'if': {'column_id': ['Project ID', 'Samples', 'Experiments']},
                           'border': '1px solid black', 'font_size': '12px'
                      }], ), ]),








            dcc.Tab(label='Country Analysis Stats', value='tab-3', className='custom-tab', selected_className='custom-tab--selected',
                    children=[html.Br(),dbc.Row([dbc.Col(html.Label("Data Submitted to INSDC  ", id ='INSDC_seq_label', style={'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}), width=11), html.Br(),
                                                  dbc.Col(dcc.Clipboard(id="table_INSDC_copy", style={"fontSize":20, "display": "inline-block"}), align="end", width=1, className="d-grid gap-2 d-md-flex justify-content-md-end")], justify="end"),

                dash_table.DataTable(
                id='table_INSDC',
                columns=[{"name": i, "id": i} for i in INSDC_seq.columns],
                data=INSDC_seq.to_dict('records'),
                style_cell={'textAlign': 'center', 'padding': '10px', 'font_size': '10px'},
                style_header={
                    'backgroundColor': 'rgba(101,198,187,0.6)',
                },
                style_header_conditional=[
                    {
                        'if': {'column_id': ['Submissions', 'country']},
                        'color': 'black',
                        'fontWeight': 'bold',
                        'border': '1px solid black'
                    }
                ],
                style_cell_conditional=[
                    {
                        'if': {'column_id': ['Submissions', 'country']},
                        'border': '1px solid black',
                        'font_size': '14px'
                    }],),
                html.Br(),dbc.Row([dbc.Col(html.Label("Data Submitted to ENA  ", id ='country_seq_label', style={'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}), width=11), html.Br(),
                                                  dbc.Col(dcc.Clipboard(id="table_seq_copy", style={"fontSize":20, "display": "inline-block"}), align="end", width=1, className="d-grid gap-2 d-md-flex justify-content-md-end")], justify="end"),
                    dash_table.DataTable(
                  id='table_seq',
                  columns=[
                      {"name": i, "id": i, "editable": (True if i == 'Notes' or i == 'Related tickets' else False)}
                      for i in webin_seq_merge.columns],
                    editable=True,
                  data=webin_seq_merge.to_dict('records'),
                  style_cell={'textAlign': 'center', 'padding': '10px', 'font_size': '10px'},
                    style_table={'width': '100%'},
                    style_data={'whiteSpace': 'pre-line', 'lineHeight': '15px'},
                    css=[{
                    'selector': '.dash-cell div.dash-cell-value',
                    'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit; line-height: 15px'
                }],
                  style_header={
                      'backgroundColor': 'white',
                  },
                  style_header_conditional=[
                      {
                          'if': {'column_id': ['Webin Account', 'Country', 'Project', 'Samples', 'Analysis ID',
                                               'GCA ID']},
                          'color': 'black',
                          'fontWeight': 'bold',
                          'border': '1px solid black'
                      }
                  ],
                  style_cell_conditional=[
                      {'if': {'column_id': 'Notes'},
                       'width': '20%'},
                      {'if': {'column_id': 'Related tickets'},
                       'width': '20%'},
                      {
                          'if': {'column_id': ['Webin Account', 'Country', 'Project', 'Samples', 'Analysis ID',
                                               'GCA ID']},
                          'border': '1px solid black',
                          'font_size': '14px'
                      }],),
                  html.Button(id="webin-seq-save-button", children="Save Notes", n_clicks=0),
                  html.Div(id="output-seq-1"),


                html.Br(), dbc.Row([dbc.Col(html.Div([
                                        html.Label("Detailed view for ENA Data  ", id='project_seq_label', style={'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}), html.Br(),
                                        html.Label("Choose a Webin id from the dropdown to view its content",id='project_seq_sublabel', style={'color': 'Black', 'fontWeight': 'bold', 'fontSize': 12})]), width=11),
                                        dbc.Col(dcc.Clipboard(id="table_project_copy", style={"fontSize":20, "display": "inline-block"}), align="end", width=1, className="d-grid gap-2 d-md-flex justify-content-md-end")], justify="end"),
                dcc.Dropdown(id='webin-seq-dropdown', options=[{'label': i, 'value': i} for i in project_seq_merge['Webin Account'].unique()], placeholder="Select a Webin ID", value='United Kingdom'),

                dash_table.DataTable(
                  id='webin_seq-table',
                  columns=[{"name": i, "id": i,
                            "editable": (True if i == 'Notes' or i == 'Related tickets' else False)} for i in
                           project_seq_merge.drop(['Webin Account', 'Country'], axis=1).columns],
                    editable=True,
                  data=project_seq_merge.to_dict('records'),
                  style_cell={'textAlign': 'center', 'font_size': '10px', 'padding': '1px'},
                    style_table={'width': '100%'},
                    style_data={'whiteSpace': 'pre-line', 'lineHeight': '15px'},
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit; line-height: 15px'
                    }],
                  style_header={
                      'backgroundColor': 'white'
                  },
                  style_header_conditional=[
                      {
                          'if': {'column_id': ['Project ID', 'Samples', 'Analysis ID', 'GCA ID']},

                          'color': 'black',
                          'fontWeight': 'bold',
                          'border': '1px solid black'
                      }
                  ],
                  style_cell_conditional=[
                      {'if': {'column_id': 'Notes'},
                       'width': '20%'},  # 'overflow': 'hidden', 'textOverflow': 'ellipsis', 'maxWidth': 0},
                      {'if': {'column_id': 'Related tickets'},
                       'width': '20%'},
                      {
                          'if': {'column_id': ['Project ID', 'Samples', 'Analysis ID', 'GCA ID']},
                           'border': '1px solid black',
                          'font_size': '12px'
                      }
                  ],

                ),
                html.Button(id="project-seq-save-button", children="Save Notes", n_clicks=0),
                html.Div(id="output-seq-2"),# children="Press button to save changes to Notes"),

                html.Br(), dbc.Row([dbc.Col(html.Div([
                                        html.Label("Center Names List  ", id='centerName_seq_label', style={'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}), html.Br(),
                                        html.Label("Choose a Project ID from the dropdown to view the associated center names",id='centerName_seq_sublabel', style={'color': 'Black', 'fontWeight': 'bold', 'fontSize': 12})]), width=11),
                                        dbc.Col(dcc.Clipboard(id="table_centerName_seq_copy", style={"fontSize":20, "display": "inline-block"}), align="end", width=1, className="d-grid gap-2 d-md-flex justify-content-md-end")], justify="end"),

                dcc.Dropdown(id='centerName-seq-dropdown',
                           options=[{'label': i, 'value': i} for i in
                                    project_seq_merge[
                                        'Project ID'].unique()], placeholder="Select a Project ID",
                           value='select'),

                dash_table.DataTable(
                  id='centerName-seq-table',
                  columns=[
                      {"name": i, "id": i}
                      for i in
                      center_names_seq.drop(['Webin Account', 'Country'],
                                        axis=1).columns],
                  data=center_names_seq.to_dict('records'),
                  style_cell={'textAlign': 'center',
                              'font_size': '10px', 'padding': '1px'},
                  style_header={
                      'backgroundColor': 'white'
                  },
                  style_header_conditional=[
                      {
                          'if': {'column_id': ['Project ID', 'Samples',
                                               'Experiments']},

                          'color': 'black',
                          'fontWeight': 'bold',
                          'border': '1px solid black'
                      }
                  ],
                  style_cell_conditional=[

                      {
                          'if': {'column_id': ['Project ID', 'Samples',
                                               'Experiments']},

                          'border': '1px solid black',
                          'font_size': '12px'
                      }
                  ],

                ),
                ]),

                ])
            ]), width={"size": 10, "offset": 1})]),
                          ], className="pad-row")#])
    ], fluid=True)


    #])

    return row



app = dash.Dash()
app.layout = dashboard




@app.callback(
    Output('country-dropdown', 'options'),
    Output('country-dropdown', 'value'),
    Input('interval-component', 'n_intervals')

)
def update_metrics(n):
    seq_df =pd.read_csv(f'{args.file}/API.sequence.output.recent.csv', sep=",").dropna()
    read_df = pd.read_csv(f'{args.file}/API.reads.output.recent.csv', sep=",").dropna()
    country_inner_join = pd.merge(seq_df, read_df, on='country', how='outer')
    country_inner_join1 = country_inner_join.where(pd.notnull(country_inner_join), 0)
    country_inner_join_mod = country_inner_join1.rename(
        columns={'Submission Date_x': 'Sequences Submission Date', 'Submissions_x': 'Sequences Submissions',
                 'Submission Date_y': 'Reads Submission Date', 'Submissions_y': 'Reads Submissions'})
    country_options = [{'label': i, 'value': i} for i in country_inner_join_mod['country'].unique()]
    print(seq_df)
    dashboard()
    return country_options, country_options[0]['value']


@app.callback(
    Output("table_INSDC_copy", "content"),
    Output("table_seq_copy", "content"),
    Output("table_project_copy", "content"),
    Output("table_centerName_seq_copy", "content"),
    Output("centerName_reads_copy", "content"),
    Output("project_reads_copy", "content"),
    Output("webin_reads_copy", "content"),

    Input("table_INSDC_copy", "n_clicks"),
    Input("table_seq_copy", "n_clicks"),
    Input("table_project_copy", "n_clicks"),
    Input("table_centerName_seq_copy", "n_clicks"),
    Input("centerName_reads_copy", "n_clicks"),
    Input("project_reads_copy", "n_clicks"),
    Input("webin_reads_copy", "n_clicks"),
    State("table_INSDC", "data"),
    State("table_seq", "data"),
    State("webin_seq-table", "data"),
    State("centerName-seq-table", "data"),
    State("centerName-reads-table", "data"),
    State("webin-table", "data"),
    State("table", "data"),
)
def custom_copy(n_INSDC,n_webin_seq,n_project_seq,n_CenterName_seq,n_CenterName_reads,n_project_reads,n_webin_reads, INSDC_data, webin_seq_data, project_seq_data, centerName_seq_data, centerName_reads_data, project_reads_data, webin_reads_data ):
    INSDC_dff = pd.DataFrame(INSDC_data)
    dff_webin_seq = pd.DataFrame(webin_seq_data)
    dff_project_seq = pd.DataFrame(project_seq_data)
    dff_centerName_seq = pd.DataFrame(centerName_seq_data)
    dff_centerName_reads = pd.DataFrame(centerName_reads_data)
    project_reads_data = pd.DataFrame(project_reads_data)
    webin_reads_data = pd.DataFrame(webin_reads_data)
    # See options for .to_csv() or .to_excel() or .to_string() in the  pandas documentation
    return INSDC_dff.to_csv(index=False), dff_webin_seq.to_csv(index=False), dff_project_seq.to_csv(index=False), dff_centerName_seq.to_csv(index=False), dff_centerName_reads.to_csv(index=False), project_reads_data.to_csv(index=False), webin_reads_data.to_csv(index=False) # includes headers




@app.callback(
    Output('country-graph', 'figure'),
    Output('country-reads_graph', 'figure'),
    Input('country-dropdown', 'value'),
    Input('interval-component', 'n_intervals'),

)

def update_graph(selected_country,n):
    seq_df =pd.read_csv(f'{args.file}/API.sequence.output.recent.csv', sep=",").dropna()
    read_df = pd.read_csv(f'{args.file}/API.reads.output.recent.csv', sep=",").dropna()
    country_inner_join = pd.merge(seq_df, read_df, on='country', how='outer')
    country_inner_join1 = country_inner_join.where(pd.notnull(country_inner_join), 0)
    country_inner_join_mod = country_inner_join1.rename(
        columns={'Submission Date_x': 'Sequences Submission Date', 'Submissions_x': 'Sequences Submissions',
                 'Submission Date_y': 'Reads Submission Date', 'Submissions_y': 'Reads Submissions'})
    now = datetime.datetime.now()
    now_str = now.strftime("%y-%m-%d")
    filtered_country=country_inner_join_mod[country_inner_join_mod['country']==selected_country]
    filtered_country_seq_mod = filtered_country.query ("`Sequences Submissions` > 0").drop_duplicates(subset="Sequences Submission Date")
    total_submissions =filtered_country_seq_mod['Sequences Submissions'].sum()
    if filtered_country_seq_mod['Sequences Submissions'].empty == True:
        line_fig = {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "No Sequence data found",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            }
        }
    else:
        line_fig=go.Figure(data=[go.Scatter(x=filtered_country_seq_mod['Sequences Submission Date'],y=filtered_country_seq_mod['Sequences Submissions'],  name=f'Sequence Submissions in {selected_country}', mode='markers', marker=dict(
            size=filtered_country_seq_mod['Sequences Submissions'],
            color = filtered_country_seq_mod['Sequences Submissions'],
            sizemode='area',
            sizeref=2.*max(filtered_country_seq_mod['Sequences Submissions'])/(30.**2),
            sizemin=1
        ), hovertemplate="Country=%s<br>Submission Date=%%{x}<br>Submissions=%%{y}<extra></extra>"% selected_country)])
        line_fig.update_xaxes(
            ticklabelmode="period",
            rangeslider_visible = True,
            tickformatstops = [
            dict(dtickrange=[None, 1000], value="%H:%M:%S.%L"),
            dict(dtickrange=[1000, 60000], value="%H:%M:%S"),
            dict(dtickrange=[60000, 3600000], value="%H:%M"),
            dict(dtickrange=[3600000, 86400000], value="%H:%M"),
            dict(dtickrange=[86400000, 604800000], value="%e. %b"),
            dict(dtickrange=[604800000, "M1"], value="%e. %b"),
            ]
        )
        line_fig.update_xaxes(title_text="Submissions Date")
        line_fig.update_yaxes(title_text="Submissions")
        line_fig.update_layout(xaxis_range=['2020-01-01',now_str])
        line_fig.update_layout(
            title=f'Public Sequence Submissions in {selected_country} with total submissions of {int(total_submissions)} sequences',
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="RebeccaPurple"
            )
        )

    filtered_country_reads = country_inner_join_mod[country_inner_join_mod['country'] == selected_country]
    filtered_country_reads_mod = filtered_country_reads.query("`Reads Submissions` > 0").drop_duplicates(subset="Reads Submission Date")

    total_submissions_reads = filtered_country_reads_mod['Reads Submissions'].sum()
    if filtered_country_reads_mod['Sequences Submissions'].empty == True:
        line_fig_reads = {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "No read data found",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            }
        }

    else:
        line_fig_reads = go.Figure(data=[go.Scatter(x=filtered_country_reads_mod['Reads Submission Date'],
                                              y=filtered_country_reads_mod['Reads Submissions'],
                                              name=f'Reads Submissions in {selected_country}', mode='markers',
                                              marker=dict(
                                                  size=filtered_country_reads_mod['Reads Submissions'],
                                                  color=filtered_country_reads_mod['Reads Submissions'],
                                                  sizemode='area',
                                                  sizeref=2. * max(filtered_country_reads_mod['Reads Submissions']) / (
                                                              30. ** 2),
                                                  sizemin=1
                                              ),
                                              hovertemplate="Country=%s<br>Submission Date=%%{x}<br>Submissions=%%{y}<extra></extra>" % selected_country)])
        line_fig_reads.update_xaxes(
            ticklabelmode="period",
            rangeslider_visible=True,
            tickformatstops=[
                dict(dtickrange=[None, 1000], value="%H:%M:%S.%L"),
                dict(dtickrange=[1000, 60000], value="%H:%M:%S"),
                dict(dtickrange=[60000, 3600000], value="%H:%M"),
                dict(dtickrange=[3600000, 86400000], value="%H:%M"),
                dict(dtickrange=[86400000, 604800000], value="%e. %b"),
                dict(dtickrange=[604800000, "M1"], value="%e. %b"),
            ]
        )
        line_fig_reads.update_xaxes(title_text="Submissions Date")
        line_fig_reads.update_yaxes(title_text="Submissions")
        line_fig_reads.update_layout(xaxis_range=['2020-01-01', now_str])
        line_fig_reads.update_layout(
            title=f'Public Read Submissions in {selected_country} with total submissions of {int(total_submissions_reads)} reads',
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="RebeccaPurple"
            )
        )

    return line_fig,line_fig_reads

@app.callback(
    Output('table', 'data'),
    Output('webin-table', 'data'),
    Output('webin-dropdown', 'options'),
    Output('table_seq', 'data'),
    Output('webin_seq-table', 'data'),
    Output('webin-seq-dropdown', 'options'),
    Output('table', 'style_header'),
    Output('webin-table', 'style_header'),
    Output('table_seq', 'style_header'),
    Output('webin_seq-table', 'style_header'),
    Output('webin-dropdown', 'style'),
    Output('webin-seq-dropdown', 'style'),
    Output('country_seq_label', 'style'),
    Output('table_seq_copy', 'style'),
    Output('webin-seq-save-button', 'style'),
    Output('project_seq_label', 'style'),
    Output('project_seq_sublabel', 'style'),
    Output('table_project_copy', 'style'),
    Output('project-seq-save-button', 'style'),
    Output('centerName_seq_label', 'style'),
    Output('centerName_seq_sublabel', 'style'),
    Output('table_centerName_seq_copy', 'style'),
    Output('webin_reads_label', 'style'),
    Output('webin_reads_sublabel', 'style'),
    Output('project-save-button', 'style'),
    Output('centerName_reads_label', 'style'),
    Output('centerName_reads_sublabel', 'style'),
    Output('centerName_reads_copy', 'style'),

    Output('table', 'style_table'),
    Output('webin-table', 'style_table'),
    Output('table_seq', 'style_table'),
    Output('webin_seq-table', 'style_table'),


    Input('country-dropdown', 'value'),
    Input('webin-dropdown', 'value'),
    Input('webin-seq-dropdown', 'value'),
    Input('interval-component', 'n_intervals')
    )

def update_stat_table (selected_country, webin_id,webin_seq_id, n):
    webin_notes = pd.read_csv(f'{args.file}/webin_notes.csv')
    webin_seq_notes = pd.read_csv(f'{args.file}/webin_seq_notes.csv')
    #SQL_reads = upload_df[2]
    webin_count_merge_final = upload_df[2]
    project_count_merge_final = upload_df[3]
    webin_seq = upload_df[4]
    project_seq = upload_df[5]

    webin_count_merge = pd.merge(webin_count_merge_final, webin_notes, on=['Webin Account', 'Country'], how='outer')
    webin_seq_merge = pd.merge(webin_seq, webin_seq_notes, on=['Webin Account', 'Country'], how='outer')


    project_notes = pd.read_csv(f'{args.file}/project_notes.csv')
    project_seq_notes = pd.read_csv(f'{args.file}/project_seq_notes.csv')

    project_count_merge = pd.merge(project_count_merge_final, project_notes,
                                   on=['Webin Account', 'Project ID', 'Country'], how='outer')
    project_seq_merge = pd.merge(project_seq, project_seq_notes, on=['Webin Account', 'Project ID', 'Country'],
                                 how='outer')

    filtered_sql_reads = webin_count_merge[webin_count_merge['Country'] == selected_country]
    filtered_sql_seq = webin_seq_merge[webin_seq_merge['Country'] == selected_country]
    filtered_country_reads = project_count_merge[project_count_merge['Country'] == selected_country]
    filtered_country_seq = project_seq_merge[project_seq_merge['Country'] == selected_country]
    filtered_webin_reads =  filtered_country_reads [filtered_country_reads['Webin Account'] == webin_id]
    filtered_webin_seq = filtered_country_seq[filtered_country_seq['Webin Account'] == webin_seq_id]
    data = filtered_sql_reads.to_dict('records')
    data_seq = filtered_sql_seq.to_dict('records')
    webin_data = filtered_webin_reads.to_dict('records')
    webin_data_seq = filtered_webin_seq.to_dict('records')

    webin_options = [{'label': i, 'value': i} for i in filtered_country_reads['Webin Account'].unique()]
    webin_seq_options = [{'label': i, 'value': i} for i in filtered_country_seq['Webin Account'].unique()]


    if filtered_webin_reads.empty:
        webin_display_reads_header_style = { 'backgroundColor': 'rgba(101,198,187,0.6)', 'display': 'none'}
        project_reads_button = {'display': 'none'}
        centerName_reads_lable = {'display': 'none'}
        centerName_sublabel_reads = {'display': 'none'}
        centerName_reads_clipboard = {'display': 'none'}
        scroll_bar_reads_project = {'display': 'none'}

    else:
        webin_display_reads_header_style = {'backgroundColor': 'rgba(101,198,187,0.6)'}
        project_reads_button = None
        centerName_reads_lable = {'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}
        centerName_sublabel_reads = {'color': 'Black', 'fontWeight': 'bold', 'fontSize': 12}
        centerName_reads_clipboard = {"fontSize": 20, "display": "inline-block"}
        scroll_bar_reads_project = {'width': '100%', 'overflowX': 'scroll'}


    if filtered_webin_seq.empty:
        webin_display_seq_header_style = { 'backgroundColor': 'rgba(101,198,187,0.6)', 'display': 'none'}
        centerName_label_seq = {'display': 'none'}
        centerName_sublabel_seq = {'display': 'none'}
        centerName_seq_clipboard = {'display': 'none'}
        project_seq_button = {'display': 'none'}
        scroll_bar_seq_project = {'display': 'none'}

    else:
        webin_display_seq_header_style = {'backgroundColor': 'rgba(101,198,187,0.6)'}
        centerName_label_seq = {'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}
        centerName_sublabel_seq = {'color': 'Black', 'fontWeight': 'bold', 'fontSize': 12}
        centerName_seq_clipboard = {"fontSize": 20, "display": "inline-block"}
        project_seq_button = None
        scroll_bar_seq_project = {'width': '100%', 'overflowX': 'scroll'}


    if filtered_country_reads.empty:
        webin_display_country_reads_header_style = {'backgroundColor': 'rgba(101,198,187,0.6)', 'display': 'none'}
        webin_dropdown_reads_style = {'display': 'none'}
        webin_label_reads = {'display': 'none'}
        webin_sublabel_reads = {'display': 'none'}
        scroll_bar_reads_webin = {'display': 'none'}
    else:
        webin_display_country_reads_header_style = {'backgroundColor': 'rgba(101,198,187,0.6)'}
        webin_dropdown_reads_style = None
        webin_label_reads = {'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}
        webin_sublabel_reads = {'color': 'Black', 'fontWeight': 'bold', 'fontSize': 12}
        scroll_bar_reads_webin = {'width': '100%', 'overflowX': 'scroll'}

    if filtered_country_seq.empty:
        webin_display_country_seq_header_style = {'backgroundColor': 'rgba(101,198,187,0.6)', 'display': 'none'}
        webin_dropdown_seq_style = {'display': 'none'}
        webin_label_seq = {'display': 'none'}
        webin_seq_clipboard = {'display': 'none'}
        webin_seq_button = {'display': 'none'}
        project_label_seq = {'display': 'none'}
        project_sublabel_seq = {'display': 'none'}
        project_seq_clipboard = {'display': 'none'}
        scroll_bar_seq_webin = {'display': 'none'}

    else:
        webin_display_country_seq_header_style = {'backgroundColor': 'rgba(101,198,187,0.6)'}
        webin_dropdown_seq_style = None
        webin_label_seq = {'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}
        webin_seq_clipboard = {"fontSize": 20, "display": "inline-block"}
        webin_seq_button = None
        project_label_seq = {'color': 'Black', 'fontWeight': 'bold', 'fontSize': 20}
        project_sublabel_seq = {'color': 'Black', 'fontWeight': 'bold', 'fontSize': 12}
        project_seq_clipboard = {"fontSize": 20, "display": "inline-block"}
        scroll_bar_seq_webin = {'width': '100%', 'overflowX': 'scroll'}




    return  data, webin_data , webin_options,data_seq,webin_data_seq,webin_seq_options,\
            webin_display_country_reads_header_style,webin_display_reads_header_style, webin_display_country_seq_header_style, webin_display_seq_header_style, \
            webin_dropdown_reads_style, webin_dropdown_seq_style, webin_label_seq, webin_seq_clipboard, webin_seq_button, project_label_seq, project_sublabel_seq, project_seq_clipboard, project_seq_button, \
            centerName_label_seq, centerName_sublabel_seq, centerName_seq_clipboard, webin_label_reads, webin_sublabel_reads, project_reads_button, centerName_reads_lable, centerName_sublabel_reads, centerName_reads_clipboard, \
            scroll_bar_reads_webin, scroll_bar_reads_project,scroll_bar_seq_webin,scroll_bar_seq_project



@app.callback(
    Output('table_INSDC', 'data'),
    Input('country-dropdown', 'value'),
    Input('interval-component', 'n_intervals')
    )

def update_INSDC_stat_table (selected_country, n):
    INSDC_df = upload_df[6]
    INSDC_seq = INSDC_df.drop('Submission Date', axis=1).groupby(by='country')['Submissions'].sum().reset_index(name='Submissions')


    filtered_sql = INSDC_seq[INSDC_seq['country'] == selected_country]
    data = filtered_sql.to_dict('records')

    return data

@app.callback(
    Output('centerName-reads-table', 'data'),
    Output('centerName-reads-dropdown', 'options'),
    Output('centerName-seq-table', 'data'),
    Output('centerName-seq-dropdown', 'options'),
    Output('centerName-seq-table', 'style_header'),
    Output('centerName-reads-table', 'style_header'),
    Output('centerName-seq-dropdown', 'style'),
    Output('centerName-reads-dropdown', 'style'),
    Input('country-dropdown', 'value'),
    Input('webin-dropdown', 'value'),
    Input('centerName-reads-dropdown', 'value'),
    Input('webin-seq-dropdown', 'value'),
    Input('centerName-seq-dropdown', 'value'),
    Input('interval-component', 'n_intervals')
    )

def update_centerName_stat_table (selected_country, selected_webin, selected_project, selected_webin_seq, selected_project_seq, n):
    center_names = upload_df[7]

    filtered_data_country = center_names[center_names['Country'] == selected_country]
    filtered_data_webin = filtered_data_country[filtered_data_country['Webin Account'] == selected_webin]
    filtered_data = filtered_data_webin[filtered_data_webin['Project ID'] == selected_project]
    filtered_data_dropdown = filtered_data_country[filtered_data_country['Webin Account'] == selected_webin]
    data = filtered_data.to_dict('records')
    project_options = [{'label': i, 'value': i} for i in filtered_data_dropdown['Project ID'].unique()]

    center_names_seq = upload_df[8]

    filtered_data_seq_country = center_names_seq[center_names_seq['Country'] == selected_country]
    filtered_data_webin_seq = filtered_data_seq_country[filtered_data_seq_country['Webin Account'] == selected_webin_seq]
    filtered_data_seq = filtered_data_webin_seq[filtered_data_webin_seq['Project ID'] == selected_project_seq]
    filtered_data_dropdown_seq = filtered_data_seq_country[filtered_data_seq_country['Webin Account'] == selected_webin_seq]
    data_seq = filtered_data_seq.to_dict('records')
    project_options_seq = [{'label': i, 'value': i} for i in filtered_data_dropdown_seq['Project ID'].unique()]

    if filtered_data_seq.empty:
        centerName_display_seq_header_style = { 'backgroundColor': 'rgba(101,198,187,0.6)', 'display': 'none'}

    else:
        centerName_display_seq_header_style = {'backgroundColor': 'rgba(101,198,187,0.6)'}


    if filtered_data.empty:
        centerName_display_reads_header_style = {'display': 'none'}
    else:
        centerName_display_reads_header_style = {'backgroundColor': 'rgba(101,198,187,0.6)'}


    if filtered_data_dropdown.empty:
        centerName_dropdown_reads_style = {'display': 'none'}
    else:
        centerName_dropdown_reads_style = {'backgroundColor': 'rgba(101,198,187,0.6)'}

    if filtered_data_dropdown_seq.empty:
        centerName_dropdown_seq_style = {'display': 'none'}
    else:
        centerName_dropdown_seq_style = {'backgroundColor': 'rgba(101,198,187,0.6)'}

    return data, project_options, data_seq, project_options_seq, centerName_display_seq_header_style, centerName_display_reads_header_style,\
           centerName_dropdown_seq_style,centerName_dropdown_reads_style



@app.callback(
        Output("output-1","children"),
        Output("output-seq-1","children"),
        [Input("webin-save-button","n_clicks")],
        [Input("webin-seq-save-button","n_clicks")],
        [State("table","data")],
        [State("table_seq","data")]
        )

def selected_webin_data_to_csv(nclicks, nclicks_seq,sub_table, sub_table_seq):
    if nclicks == 0 or nclicks_seq == 0 :
        #return "No Data Submitted", "No Data Submitted"
        raise PreventUpdate #blocks callback from running


    else:
        webin_notes = pd.read_csv(f'{args.file}/webin_notes.csv')
        webin_seq_notes = pd.read_csv(f'{args.file}/webin_seq_notes.csv')

        webin_count_merge = pd.merge(webin_count_merge_final, webin_notes, on=['Webin Account', 'Country'], how='outer')
        webin_seq_merge = pd.merge(webin_seq, webin_seq_notes, on=['Webin Account', 'Country'], how='outer')

        sub_table_df = pd.DataFrame(sub_table)
        sub_table_seq_df = pd.DataFrame(sub_table_seq)
        sub_table_df_mod_note = formatting_notes_tickets(sub_table_df,'Notes')
        sub_table_seq_df_mod_note = formatting_notes_tickets(sub_table_seq_df, 'Notes')
        sub_table_df_mod = formatting_notes_tickets(sub_table_df_mod_note,'Related tickets')
        sub_table_seq_df_mod = formatting_notes_tickets(sub_table_seq_df_mod_note, 'Related tickets')

        webin_count_merge_note_raw = webin_count_merge[
            ['Webin Account', 'Country', 'Notes', 'Related tickets']].merge(
            sub_table_df_mod[['Webin Account', 'Country', 'Notes', 'Related tickets']], on=['Webin Account', 'Country'],
            how='left')
        webin_seq_merge_note_raw = webin_seq_merge[
            ['Webin Account', 'Country', 'Notes', 'Related tickets']].merge(
            sub_table_seq_df_mod[['Webin Account', 'Country', 'Notes', 'Related tickets']], on=['Webin Account', 'Country'],
            how='left')

        webin_count_merge_note_formatted = formatting_x_y(webin_count_merge_note_raw,'Notes_x','Notes_y')
        webin_seq_merge_note_formatted = formatting_x_y(webin_seq_merge_note_raw, 'Notes_x', 'Notes_y')
        webin_count_merge_all_formatted = formatting_x_y(webin_count_merge_note_formatted,'Related tickets_x','Related tickets_y')
        webin_seq_merge_all_formatted = formatting_x_y(webin_seq_merge_note_formatted, 'Related tickets_x',
                                                         'Related tickets_y')

        webin_count_merge_note = webin_count_merge_all_formatted.where(pd.notnull(webin_count_merge_all_formatted), '')
        webin_seq_merge_note = webin_seq_merge_all_formatted.where(pd.notnull(webin_seq_merge_all_formatted), '')

        webin_count_merge_note['Notes'] = webin_count_merge_note['Notes_x'].astype(str) + webin_count_merge_note['Notes_y'].astype(str)
        webin_seq_merge_note['Notes'] = webin_seq_merge_note['Notes_x'].astype(str) + webin_seq_merge_note[
            'Notes_y'].astype(str)

        webin_count_merge_note['Related tickets'] = webin_count_merge_note['Related tickets_x'].astype(str) + \
                                                    webin_count_merge_note['Related tickets_y'].astype(str)

        webin_seq_merge_note['Related tickets'] = webin_seq_merge_note['Related tickets_x'].astype(str) + \
                                                    webin_seq_merge_note['Related tickets_y'].astype(str)

        pd.DataFrame(webin_count_merge_note[['Webin Account', 'Country', 'Notes', 'Related tickets']]).to_csv(
            f'{args.file}/webin_notes.csv', index=False)

        pd.DataFrame(webin_seq_merge_note[['Webin Account', 'Country', 'Notes', 'Related tickets']]).to_csv(
            f'{args.file}/webin_seq_notes.csv', index=False)

        return "Data Submitted", "Data Submitted"



@app.callback(
    Output("output-2", "children"),
    Output("output-seq-2", "children"),
    [Input("project-save-button", "n_clicks")],
    [Input("project-seq-save-button", "n_clicks")],
    [State("webin-table", "data")],
    [State("webin_seq-table", "data")]
)
def selected_project_data_to_csv(project_nclicks,project_seq_nclicks, project_sub_table, project_seq_sub_table):
    if project_nclicks == 0 or project_seq_nclicks == 0:
        #return "No Data Submitted", "No Data Submitted"
        raise PreventUpdate #blocks callback from running

    else:
        project_notes = pd.read_csv(f'{args.file}/project_notes.csv')

        project_count_merge = pd.merge(project_count_merge_final, project_notes, on=['Webin Account', 'Project ID', 'Country'], how='outer')

        project_seq_notes = pd.read_csv(f'{args.file}/project_seq_notes.csv')

        project_seq_merge = pd.merge(project_seq, project_seq_notes, on=['Webin Account', 'Project ID', 'Country'],
                                     how='outer')

        project_sub_table_df = pd.DataFrame(project_sub_table)
        project_sub_table_df_mod_note = formatting_notes_tickets(project_sub_table_df, 'Notes')
        project_sub_table_df_mod = formatting_notes_tickets(project_sub_table_df_mod_note, 'Related tickets')

        project_seq_sub_table_df = pd.DataFrame(project_seq_sub_table)
        project_seq_sub_table_df_mod_note = formatting_notes_tickets(project_seq_sub_table_df, 'Notes')
        project_seq_sub_table_df_mod = formatting_notes_tickets(project_seq_sub_table_df_mod_note, 'Related tickets')


        project_count_merge_note_raw = project_count_merge[
            ['Webin Account','Project ID', 'Country', 'Notes', 'Related tickets']].merge(
            project_sub_table_df_mod[['Webin Account', 'Project ID', 'Country', 'Notes', 'Related tickets']], on=['Webin Account','Project ID', 'Country'],
            how='left')

        project_seq_merge_note_raw = project_seq_merge[
            ['Webin Account', 'Project ID', 'Country', 'Notes', 'Related tickets']].merge(
            project_seq_sub_table_df_mod[['Webin Account', 'Project ID', 'Country', 'Notes', 'Related tickets']],
            on=['Webin Account', 'Project ID', 'Country'],
            how='left')


        project_count_merge_note_formatted = formatting_x_y(project_count_merge_note_raw, 'Notes_x', 'Notes_y')
        project_count_merge_all_formatted = formatting_x_y(project_count_merge_note_formatted, 'Related tickets_x',
                                                         'Related tickets_y')

        project_seq_merge_note_formatted = formatting_x_y(project_seq_merge_note_raw, 'Notes_x', 'Notes_y')
        project_seq_merge_all_formatted = formatting_x_y(project_seq_merge_note_formatted, 'Related tickets_x',
                                                           'Related tickets_y')

        project_count_merge_note = project_count_merge_all_formatted.where(pd.notnull(project_count_merge_all_formatted), '')

        project_count_merge_note['Notes'] = project_count_merge_note['Notes_x'].astype(str) + project_count_merge_note[
            'Notes_y'].astype(str)

        project_count_merge_note['Related tickets'] = project_count_merge_note['Related tickets_x'].astype(str) + \
                                                    project_count_merge_note['Related tickets_y'].astype(str)

        project_seq_merge_note = project_seq_merge_all_formatted.where(
            pd.notnull(project_seq_merge_all_formatted), '')

        project_seq_merge_note['Notes'] = project_seq_merge_note['Notes_x'].astype(str) + project_seq_merge_note[
            'Notes_y'].astype(str)

        project_seq_merge_note['Related tickets'] = project_seq_merge_note['Related tickets_x'].astype(str) + \
                                                      project_seq_merge_note['Related tickets_y'].astype(str)


        pd.DataFrame(project_count_merge_note[['Webin Account', 'Project ID', 'Country', 'Notes', 'Related tickets']]).to_csv(
            f'{args.file}/project_notes.csv', index=False)

        pd.DataFrame(
            project_seq_merge_note[['Webin Account', 'Project ID', 'Country', 'Notes', 'Related tickets']]).to_csv(
            f'{args.file}/project_seq_notes.csv', index=False)


        return "Data Submitted", "Data Submitted"


if __name__ == '__main__':
    app.run_server(debug=True, host='10.42.28.202', port='8080')





