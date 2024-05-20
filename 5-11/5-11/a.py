import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load your DataFrame for pages
df_pages = pd.read_csv('./Pages.csv')
df_pages['CTR'] = pd.to_numeric(df_pages['CTR'].str.rstrip('%')) / 100

# Load additional DataFrames
df_countries = pd.read_csv('./Countries.csv')
df_countries['CTR'] = pd.to_numeric(df_countries['CTR'].str.rstrip('%')) / 100
df_queries = pd.read_csv('./Queries.csv')
df_queries['CTR'] = pd.to_numeric(df_queries['CTR'].str.rstrip('%')) / 100
df_search_appearance = pd.read_csv('./Search_appearance.csv')
df_search_appearance['CTR'] = pd.to_numeric(df_search_appearance['CTR'].str.rstrip('%')) / 100
df_search_appearance = df_search_appearance.sort_values(by='Clicks', ascending=False)
df_dates = pd.read_csv('./Dates.csv')

# Convert 'CTR' column to numeric in df_dates
df_dates['CTR'] = pd.to_numeric(df_dates['CTR'].str.rstrip('%')) / 100

# Sample data for devices
data = {
    "Device": ["Mobile", "Desktop", "Tablet"],
    "Clicks": [42014, 22513, 1019],
    "Impressions": [639944, 526264, 10050],
    "CTR": ["6.57%", "4.28%", "10.14%"],
    "Position": [18.81, 44.08, 11.4]
}
df_devices = pd.DataFrame(data)
df_devices['CTR'] = df_devices['CTR'].str.rstrip('%').astype(float) / 100

# Calculate overall performance metrics
total_clicks = df_dates['Clicks'].sum()
total_impressions = df_dates['Impressions'].sum()
average_ctr = (total_clicks / total_impressions) * 100
average_position = df_dates['Position'].mean()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Interactive Dashboard Example'),

    # CSS styles
    html.Style('''
        .metrics-container {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }

        .metric-card {
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            width: 20%;
        }

        .metric-value {
            font-size: 24px;
            font-weight: bold;
        }
    '''),

    # Overall performance metrics
    html.Div([
        html.Div([
            html.H4('Total Clicks'),
            html.P(f"{total_clicks:,.0f}", className='metric-value')
        ], className='metric-card'),

        html.Div([
            html.H4('Total Impressions'),
            html.P(f"{total_impressions:,.0f}", className='metric-value')
        ], className='metric-card'),

        html.Div([
            html.H4('Average CTR'),
            html.P(f"{average_ctr:.1f}%", className='metric-value')
        ], className='metric-card'),

        html.Div([
            html.H4('Average Position'),
            html.P(f"{average_position:.1f}", className='metric-value')
        ], className='metric-card'),
    ], className='metrics-container'),

    dcc.Tabs([
        dcc.Tab(label='Clicks Over Time', children=[
            dcc.Graph(id='line-graph')
        ]),
        dcc.Tab(label='CTR vs Position (Pages)', children=[
            dcc.Dropdown(
                id='range-selector-pages',
                options=[{'label': range, 'value': range} for range in ['0-3', '3-10', '10-20', '20-50', '50-100']],
                value='0-3',
                clearable=False
            ),
            dcc.Graph(id='scatter-plot-pages'),
            html.Div(id='link-container', children=[
                html.A(id='link-pages', children="Click on a point to visit the page", href="", target="_blank", style={'marginTop': '20px'})
            ])
        ]),
        dcc.Tab(label='CTR vs Position (Queries)', children=[
            dcc.Dropdown(
                id='range-selector-queries',
                options=[{'label': range, 'value': range} for range in ['0-3', '3-10', '10-20', '20-50', '50-100']],
                value='0-3',
                clearable=False
            ),
            dcc.Graph(id='scatter-plot-queries'),
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
    [Input('line-graph', 'hoverData')]
)
def update_line_graph(hover_data):
    fig = px.line(df_dates, x='Date', y=['Clicks', 'Impressions', 'CTR', 'Position'], title='Clicks Over Time',
                  labels={'value': 'Metrics', 'variable': 'Metrics'})
    fig.update_traces(mode='lines+markers')
    fig.update_layout(hovermode='x unified')
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        )
    )
    # Update hover template for each trace
    fig.update_traces(selector=dict(name='Clicks'), hovertemplate="Clicks: %{y}<extra></extra>")
    fig.update_traces(selector=dict(name='Impressions'), hovertemplate="Impressions: %{y}<extra></extra>")
    fig.update_traces(selector=dict(name='CTR'), hovertemplate="CTR: %{y:.2%}<extra></extra>")
    fig.update_traces(selector=dict(name='Position'), hovertemplate="Position: %{y}<extra></extra>")
    return fig

@app.callback(
    Output('scatter-plot-pages', 'figure'),
    [Input('range-selector-pages', 'value')]
)
def update_scatter_graph_pages(selected_range):
    return create_scatter_figure(df_pages, selected_range, hover_data={'CTR': ':.2%', 'Position': True}, custom_data_col='Top pages')

@app.callback(
    [Output('link-pages', 'href'), Output('link-pages', 'children')],
    [Input('scatter-plot-pages', 'clickData')]
)
def update_link_pages(clickData):
    if clickData:
        url = clickData['points'][0]['customdata']
        return url, f"Visit: {url}"
    return "#", "Click on a point to visit the page"

@app.callback(
    Output('scatter-plot-queries', 'figure'),
    [Input('range-selector-queries', 'value')]
)
def update_scatter_graph_queries(selected_range):
    return create_scatter_figure(df_queries, selected_range, hover_data={'CTR': ':.2%', 'Position': True}, custom_data_col='Top queries')

@app.callback(
    Output('query-details', 'children'),
    [Input('scatter-plot-queries', 'clickData')]
)
def update_query_details(clickData):
    if clickData:
        point = clickData['points'][0]
        details = f"Query: {point['customdata']}\nCTR: {point['y']:.2%}\nPosition: {point['x']}"
        return details
    return "Click on a point to see the query details"

@app.callback(
    Output('bar-plot', 'figure'),
    [Input('metric-selector', 'value')]
)
def update_bar_graph(selected_metric):
    return create_bar_figure(selected_metric)

if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
