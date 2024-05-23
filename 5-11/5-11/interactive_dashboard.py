import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.express as px
import pandas as pd
import os 

# Load data
df_pages = pd.read_csv('./Pages.csv')
df_pages['CTR'] = pd.to_numeric(df_pages['CTR'].str.rstrip('%')) / 100
df_countries = pd.read_csv('./Countries.csv')
df_countries['CTR'] = pd.to_numeric(df_countries['CTR'].str.rstrip('%')) / 100
df_queries = pd.read_csv('./Queries.csv')
df_queries['CTR'] = pd.to_numeric(df_queries['CTR'].str.rstrip('%')) / 100
df_queries['Position'] = pd.to_numeric(df_queries['Position'], errors='coerce')
df_queries = df_queries.dropna(subset=['Position'])
df_search_appearance = pd.read_csv('./Search_appearance.csv')
df_search_appearance['CTR'] = pd.to_numeric(df_search_appearance['CTR'].str.rstrip('%')) / 100
df_search_appearance = df_search_appearance.sort_values(by='Clicks', ascending=False)
df_dates = pd.read_csv('./Dates.csv')
df_dates['CTR'] = pd.to_numeric(df_dates['CTR'].str.rstrip('%')) / 100

data = {
    "Device": ["Mobile", "Desktop", "Tablet"],
    "Clicks": [42014, 22513, 1019],
    "Impressions": [639944, 526264, 10050],
    "CTR": ["6.57%", "4.28%", "10.14%"],
    "Position": [18.81, 44.08, 11.4]
}
df_devices = pd.DataFrame(data)
df_devices['CTR'] = df_devices['CTR'].str.rstrip('%').astype(float) / 100

def create_bar_figure(metric):
    fig = px.bar(df_devices, x='Device', y=metric, title=f'{metric} by Device', text=metric)
    if metric == 'CTR':
        fig.update_traces(texttemplate='%{y:.2%}', textposition='outside')
    else:
        fig.update_traces(texttemplate='%{y:.2s}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    return fig

def create_search_appearance_bar():
    fig = px.bar(df_search_appearance, x='Search Appearance', y='Clicks',
                 hover_data={'Clicks': True, 'Impressions': True, 'CTR': ':.2%', 'Position': True},
                 labels={'Clicks': 'Clicks', 'Impressions': 'Impressions', 'CTR': 'CTR (%)', 'Position': 'Position'},
                 title='Search Appearance Metrics')
    return fig

def create_country_choropleth():
    fig = px.choropleth(df_countries, locations='Country', locationmode='country names',
                        color='Clicks', hover_name='Country',
                        hover_data={'Clicks': True, 'Impressions': True, 'CTR': ':.2%', 'Position': True},
                        color_continuous_scale=px.colors.sequential.Plasma,
                        labels={'Clicks': 'Clicks', 'Impressions': 'Impressions', 'CTR': 'CTR (%)', 'Position': 'Position'},
                        title='Clicks by Country')
    return fig

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Interactive Dashboard'),

    dcc.Tabs([
        dcc.Tab(label='Clicks Over Time', children=[
            dcc.Store(id='clicks-store', data=True),
            dcc.Store(id='impressions-store', data=True),
            dcc.Store(id='ctr-store', data=True),
            dcc.Store(id='position-store', data=True),
            dcc.Graph(id='line-graph')
        ]),
        dcc.Tab(label='CTR vs Position (Pages)', children=[
            dcc.Graph(id='bar-plot-pages'),
            dcc.Dropdown(
                id='range-selector-pages',
                options=[{'label': range, 'value': range} for range in ['0-3', '3-10', '10-20', '20-50', '50-100']],
                value='0-3',
                clearable=False
            ),
            dash_table.DataTable(
                id='query-table-pages',
                columns=[
                    {'name': 'Top pages', 'id': 'Top pages'},
                    {'name': 'Clicks', 'id': 'Clicks'},
                    {'name': 'Impressions', 'id': 'Impressions'},
                    {'name': 'CTR', 'id': 'CTR'},
                    {'name': 'Position', 'id': 'Position'}
                ],
                data=[],
                row_selectable='single',
                selected_rows=[],
                style_cell_conditional=[
                    {'if': {'column_id': 'Top pages'},
                     'whiteSpace': 'normal',
                     'maxWidth': '150px',
                     'overflow': 'hidden',
                     'textOverflow': 'ellipsis'}
                ],
                style_table={'height': '300px', 'overflowY': 'auto'}
            ),
            html.Div(id='link-container', children=[
                html.A(id='link-pages', children="Click on a row to visit the page", href="", target="_blank", style={'marginTop': '20px'})
            ])
        ]),
        dcc.Tab(label='CTR vs Position (Queries)', children=[
            dcc.Graph(id='bar-plot-queries'),
            dcc.Dropdown(
                id='range-selector-queries',
                options=[{'label': range, 'value': range} for range in ['0-3', '3-10', '10-20', '20-50', '50-100']],
                value='0-3',
                clearable=False
            ),
            dash_table.DataTable(
                id='query-table-queries',
                columns=[
                    {'name': 'Top queries', 'id': 'Top queries'},
                    {'name': 'Clicks', 'id': 'Clicks'},
                    {'name': 'Impressions', 'id': 'Impressions'},
                    {'name': 'CTR', 'id': 'CTR'},
                    {'name': 'Position', 'id': 'Position'}
                ],
                data=[],
                row_selectable='single',
                selected_rows=[],
                style_cell_conditional=[
                    {'if': {'column_id': 'Top queries'},
                     'whiteSpace': 'normal',
                     'maxWidth': '150px',
                     'overflow': 'hidden',
                     'textOverflow': 'ellipsis'}
                ],
                style_table={'height': '300px', 'overflowY': 'auto'}
            ),
            html.Div(id='query-details', style={'marginTop': '20px', 'whiteSpace': 'pre-line'})
        ]),
        dcc.Tab(label='Metric by Device', children=[
            dcc.Dropdown(
                id='metric-selector',
                options=[{'label': metric, 'value': metric} for metric in ['Clicks', 'Impressions', 'CTR', 'Position']],
                value='CTR',
                clearable=False
            ),
            dcc.Graph(id='bar-plot')
        ]),
        dcc.Tab(label='Search Appearance', children=[
            dcc.Graph(id='search-appearance-bar', figure=create_search_appearance_bar())
        ]),
        dcc.Tab(label='Clicks by Country', children=[
            dcc.Graph(id='country-choropleth', figure=create_country_choropleth())
        ])
    ])
])

@app.callback(
    Output('line-graph', 'figure'),
    [Input('clicks-store', 'data'),
     Input('impressions-store', 'data'),
     Input('ctr-store', 'data'),
     Input('position-store', 'data')]
)
def update_line_graph(show_clicks, show_impressions, show_ctr, show_position):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if show_clicks:
        fig.add_trace(
            go.Scatter(x=df_dates['Date'], y=df_dates['Clicks'], mode='lines+markers', name='Clicks', hovertemplate="Clicks: %{y}<extra></extra>"),
            secondary_y=False,
        )
    if show_impressions:
        fig.add_trace(
            go.Scatter(x=df_dates['Date'], y=df_dates['Impressions'], mode='lines+markers', name='Impressions', hovertemplate="Impressions: %{y}<extra></extra>"),
            secondary_y=False,
        )
    if show_ctr:
        fig.add_trace(
            go.Scatter(x=df_dates['Date'], y=df_dates['CTR'], mode='lines+markers', name='CTR', hovertemplate="CTR: %{y:.2%}<extra></extra>"),
            secondary_y=True,
        )
    if show_position:
        fig.add_trace(
            go.Scatter(x=df_dates['Date'], y=df_dates['Position'], mode='lines+markers', name='Position', hovertemplate="Position: %{y}<extra></extra>"),
            secondary_y=True,
        )

    fig.update_layout(
        title_text="Clicks Over Time",
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        )
    )

    fig.update_yaxes(title_text="Clicks and Impressions", secondary_y=False)
    fig.update_yaxes(title_text="CTR and Position", secondary_y=True)

    return fig

@app.callback(
    Output('clicks-store', 'data'),
    [Input('line-graph', 'relayoutData')],
    [State('clicks-store', 'data')]
)
def toggle_clicks_visibility(relayoutData, show_clicks):
    if relayoutData and 'clicks' in relayoutData:
        return not show_clicks
    return show_clicks

@app.callback(
    Output('impressions-store', 'data'),
    [Input('line-graph', 'relayoutData')],
    [State('impressions-store', 'data')]
)
def toggle_impressions_visibility(relayoutData, show_impressions):
    if relayoutData and 'impressions' in relayoutData:
        return not show_impressions
    return show_impressions

@app.callback(
    Output('ctr-store', 'data'),
    [Input('line-graph', 'relayoutData')],
    [State('ctr-store', 'data')]
)
def toggle_ctr_visibility(relayoutData, show_ctr):
    if relayoutData and 'ctr' in relayoutData:
        return not show_ctr
    return show_ctr

@app.callback(
    Output('position-store', 'data'),
    [Input('line-graph', 'relayoutData')],
    [State('position-store', 'data')]
)
def toggle_position_visibility(relayoutData, show_position):
    if relayoutData and 'position' in relayoutData:
        return not show_position
    return show_position

@app.callback(
    Output('query-table-pages', 'data'),
    [Input('range-selector-pages', 'value')]
)
def update_table_pages(selected_range):
    ranges = {
        '0-3': (0, 3),
        '3-10': (3, 10),
        '10-20': (10, 20),
        '20-50': (20, 50),
        '50-100': (50, 100)
    }
    low, high = ranges[selected_range]
    df_filtered = df_pages[(df_pages['Position'] > low) & (df_pages['Position'] <= high)]
    df_filtered['CTR'] = df_filtered['CTR'].apply(lambda x: f'{x:.2%}')
    return df_filtered.to_dict('records')

@app.callback(
    Output('query-table-queries', 'data'),
    [Input('range-selector-queries', 'value')]
)
def update_table_queries(selected_range):
    ranges = {
        '0-3': (0, 3),
        '3-10': (3, 10),
        '10-20': (10, 20),
        '20-50': (20, 50),
        '50-100': (50, 100)
    }
    low, high = ranges[selected_range]
    df_filtered = df_queries[(df_queries['Position'] > low) & (df_queries['Position'] <= high)]
    df_filtered['CTR'] = df_filtered['CTR'].apply(lambda x: f'{x:.2%}')
    return df_filtered.to_dict('records')

@app.callback(
    Output('bar-plot-pages', 'figure'),
    [Input('query-table-pages', 'selected_rows')],
    [State('query-table-pages', 'data')]
)
def update_bar_plot_pages(selected_rows, data):
    if selected_rows:
        selected_data = [data[i] for i in selected_rows]
        df_selected = pd.DataFrame(selected_data)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for column in ['Clicks', 'Impressions']:
            fig.add_trace(
                go.Bar(x=df_selected['Top pages'], y=df_selected[column], name=column, yaxis='y'),
                secondary_y=False,
            )
        for column in ['CTR', 'Position']:
            fig.add_trace(
                go.Scatter(x=df_selected['Top pages'], y=df_selected[column], name=column, mode='lines+markers', yaxis='y2'),
                secondary_y=True,
            )

        threshold = 2000
        if df_selected['Impressions'].max() - df_selected['Clicks'].max() < threshold:
            fig.update_yaxes(type="linear", secondary_y=False)
        else:
            fig.update_yaxes(type="log", secondary_y=False)

        fig.update_layout(
            title_text="CTR vs Position (Pages)",
            barmode='group'
        )

        fig.update_yaxes(title_text="Clicks and Impressions", secondary_y=False)
        fig.update_yaxes(title_text="CTR and Position", secondary_y=True)

        return fig
    return {}

@app.callback(
    Output('bar-plot-queries', 'figure'),
    [Input('query-table-queries', 'selected_rows')],
    [State('query-table-queries', 'data')]
)
def update_bar_plot_queries(selected_rows, data):
    if selected_rows:
        selected_data = [data[i] for i in selected_rows]
        df_selected = pd.DataFrame(selected_data)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for column in ['Clicks', 'Impressions']:
            fig.add_trace(
                go.Bar(x=df_selected['Top queries'], y=df_selected[column], name=column, yaxis='y'),
                secondary_y=False,
            )
        for column in ['CTR', 'Position']:
            fig.add_trace(
                go.Scatter(x=df_selected['Top queries'], y=df_selected[column], name=column, mode='lines+markers', yaxis='y2'),
                secondary_y=True,
            )

        threshold = 2000
        if df_selected['Impressions'].max() - df_selected['Clicks'].max() < threshold:
            fig.update_yaxes(type="linear", secondary_y=False)
        else:
            fig.update_yaxes(type="log", secondary_y=False)

        fig.update_layout(
            title_text="CTR vs Position (Queries)",
            barmode='group'
        )

        fig.update_yaxes(title_text="Clicks and Impressions", secondary_y=False)
        fig.update_yaxes(title_text="CTR and Position", secondary_y=True)

        return fig
    return {}

@app.callback(
    [Output('link-pages', 'href'), Output('link-pages', 'children')],
    [Input('query-table-pages', 'selected_rows')],
    [State('query-table-pages', 'data')]
)
def update_link_pages(selected_rows, data):
    if selected_rows:
        url = data[selected_rows[0]]['Top pages']
        return url, f"Visit: {url}"
    return "#", "Click on a row to visit the page"

@app.callback(
    Output('bar-plot', 'figure'),
    [Input('metric-selector', 'value')]
)
def update_bar_graph(selected_metric):
    return create_bar_figure(selected_metric)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=True, host='0.0.0.0', port=port)
