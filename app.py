from dash import Dash, html, dcc, Output, Input
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px  # Import Plotly Express
import requests
import os

# Load your data and create the four Plotly figures
# You can replace the file path with your actual file path
data_path = r"C:\Users\Navee\Documents\Research\Dashboard-Project\cleaned_data.csv"
df = pd.read_csv(data_path)

df['Start Time'] = pd.to_datetime(df['Start Time'])

# Modify the URL to request JSON data
# url = "https://api-generator.retool.com/mothUr/data"

# response_API = requests.get(url)

# json_data = response_API.json()

# df = pd.DataFrame(json_data)

# # print(df)

# df['Power in kWh'] = pd.to_numeric(df['Power in kWh'], errors='coerce')
# df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')
# df['Start Time'] = pd.to_datetime(df['Start Time'])

# Define a function for Figure 1
def create_figure1(selected_shift):
    if selected_shift == 'Overall':
        dff = df
    else:
        dff = df[df['Shift'] == selected_shift]

    avg_power = dff.groupby('Shift')['Power in kWh'].mean().reset_index()
    avg_duration = dff.groupby('Shift')['Duration'].mean().reset_index()

    # Define colors for each metric
    power_color = 'red'
    duration_color = 'blue'

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=avg_power['Shift'],
            y=avg_power['Power in kWh'],
            marker_color=power_color,
            name='Average Power (kWh)',
        )
    )

    fig.add_trace(
        go.Bar(
            x=avg_duration['Shift'],
            y=avg_duration['Duration'],
            marker_color=duration_color,
            name='Average Duration',
        )
    )

    fig.update_layout(
        title=f'Average Metrics for Shift {selected_shift}',
        xaxis=dict(title='Shift'),
        yaxis=dict(title='Value'),
        barmode='group',
    )

    return fig

# Define a function for Figure 2
def create_figure2(selected_shift, interval):
    if selected_shift == 'Overall':
        dff = df
    else:
        dff = df[df['Shift'] == selected_shift]

    if interval == 'Day':
        time_grouping = dff.set_index('Start Time').groupby(pd.Grouper(freq='D'))
        title = f'Cycle Counts per Day for Shift {selected_shift}'
    elif interval == 'Month':
        time_grouping = dff.set_index('Start Time').groupby(pd.Grouper(freq='M'))
        title = f'Cycle Counts per Month for Shift {selected_shift}'
    else:
        return None  # Invalid interval

    cycle_counts = time_grouping['Cycle No'].count().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cycle_counts['Start Time'],
        y=cycle_counts['Cycle No'],
        mode='lines+markers',
        name='Cycle Counts',
        line=dict(color='blue'),
        marker=dict(color='blue'),
    ))

    fig.update_layout(
        title=title,
        xaxis=dict(title='Time'),
        yaxis=dict(title='Cycle Counts'),
    )

    return fig

# Define a function for Figure 3
def create_figure3(selected_shift):
    if selected_shift == 'Overall':
        dff = df.copy()
    else:
        dff = df[df['Shift'] == selected_shift].copy()

    dff['YearMonth'] = dff['Start Time'].dt.strftime('%Y-%m')
    shift_monthly_avg = dff.groupby(['YearMonth', 'Shift'])['Cycle No'].mean().reset_index()

    fig = go.Figure()

    for shift in shift_monthly_avg['Shift'].unique():
        shift_data = shift_monthly_avg[shift_monthly_avg['Shift'] == shift]
        fig.add_trace(go.Scatter(
            x=shift_data['YearMonth'],
            y=shift_data['Cycle No'],
            mode='lines+markers',
            name=f'Shift {shift}',
        ))

    fig.update_layout(
        title='Average Cycle Count per Month',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Average Cycle Count'),
    )

    return fig

# Define a function for Figure 4
def create_figure4(selected_shift):
    if selected_shift == 'Overall':
        dff = df.copy()
    else:
        dff = df[df['Shift'] == selected_shift].copy()

    dff['YearMonth'] = dff['Start Time'].dt.strftime('%Y-%m')
    dff['YearMonthDay'] = dff['Start Time'].dt.strftime('%Y-%m-%d')

    fig = go.Figure()

    for shift in dff['Shift'].unique():
        shift_data = dff[dff['Shift'] == shift]

        daily_min = shift_data.groupby(['YearMonthDay', 'Shift'])['Cycle No'].min().reset_index()
        daily_max = shift_data.groupby(['YearMonthDay', 'Shift'])['Cycle No'].max().reset_index()

        fig.add_trace(go.Scatter(
            x=daily_min['YearMonthDay'],
            y=daily_min['Cycle No'],
            mode='lines',
            name=f'Shift {shift} (Min)',
        ))

        fig.add_trace(go.Scatter(
            x=daily_max['YearMonthDay'],
            y=daily_max['Cycle No'],
            mode='lines',
            name=f'Shift {shift} (Max)',
        ))

    fig.update_layout(
        title='Cycle Count Analysis',
        xaxis=dict(title='Date (Month/Daily)'),
        yaxis=dict(title='Cycle Count'),
    )

    return fig

# Define a function for Figure 5 (Power Consumption Pie Chart)
def create_figure5(selected_shift):
    if selected_shift == 'Overall':
        dff = df
    else:
        dff = df[df['Shift'] == selected_shift]

    power_sum = dff.groupby('Shift')['Power in kWh'].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=power_sum['Shift'],
        values=power_sum['Power in kWh'],
        hole=0.3,
    ))

    fig.update_layout(
        title=f'Power Consumption for Shift {selected_shift}',
    )

    return fig

# Define a function for Figure 6 (Line Chart)
def create_figure6():
    fig = px.line(df, x='Start Time', y='Power in kWh', color='Shift', title='Time Series Plot')
    return fig

# Create the Dash app
app = Dash(__name__, suppress_callback_exceptions=True)

server = app.server

# Define the layout for page 1
page_1_layout = html.Div([
    html.Img(src='https://res.cloudinary.com/duv0mhzrm/image/upload/v1695632928/download_qjbsfe.png', alt='Your Logo', style={'width': '200px', 'height': '100px','margin-left': '750px'}),
    html.H1(children='Nelcast Furnace-7 Analysis Report', style={'textAlign': 'center', 'color': 'blue'}),
    dcc.RadioItems(
        options=[
            {'label': 'Shift 1', 'value': 'Shift 1'},
            {'label': 'Shift 2', 'value': 'Shift 2'},
            {'label': 'Shift 3', 'value': 'Shift 3'},
            {'label': 'Overall', 'value': 'Overall'}
        ],
        value='Overall',
        id='dropdown-selection-page-1'
    ),
    dcc.RadioItems(
        options=[
            {'label': 'Day', 'value': 'Day'},
            {'label': 'Month', 'value': 'Month'}
        ],
        value='Day',
        id='interval-selection-page-1'
    ),
    html.Div([
        dcc.Graph(id='graph-content1-page-1', config={'displaylogo': False, 'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomOut2d']}),  # Figure 1 for page 1
        dcc.Graph(id='graph-content2-page-1', config={'displaylogo': False, 'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomOut2d']}),  # Figure 2 for page 1
    ], style={'display': 'flex', 'flex-direction': 'row'}),
])

# Define the layout for page 2
page_2_layout = html.Div([
    html.Img(src='https://res.cloudinary.com/duv0mhzrm/image/upload/v1695632928/download_qjbsfe.png', alt='Your Logo', style={'width': '200px', 'height': '100px','margin-left': '750px'}),
    html.H1(children='Nelcast Furnace-7 Analysis Report', style={'textAlign': 'center', 'color': 'blue'}),
    dcc.RadioItems(
        options=[
            {'label': 'Shift 1', 'value': 'Shift 1'},
            {'label': 'Shift 2', 'value': 'Shift 2'},
            {'label': 'Shift 3', 'value': 'Shift 3'},
            {'label': 'Overall', 'value': 'Overall'}
        ],
        value='Overall',
        id='dropdown-selection-page-2'
    ),
    html.Div([
        dcc.Graph(id='graph-content3-page-2', config={'displaylogo': False, 'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomOut2d']}),  # Figure 3 for page 2 (Left side)
        dcc.Graph(id='graph-content4-page-2', config={'displaylogo': False, 'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomOut2d']}),  # Figure 4 for page 2 (Right side)
    ], style={'display': 'flex', 'flex-direction': 'row'}),
])

# Define the layout for page 3
page_3_layout = html.Div([
    html.Img(src='https://res.cloudinary.com/duv0mhzrm/image/upload/v1695632928/download_qjbsfe.png', alt='Your Logo', style={'width': '200px', 'height': '100px','margin-left': '750px'}),
    html.H1(children='Nelcast Furnace-7 Analysis Report', style={'textAlign': 'center', 'color': 'blue'}),
    
    # Figure 5 (Power Consumption Pie Chart)
    dcc.Graph(id='power-pie-chart-page-3', config={'displaylogo': False, 'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomOut2d']}),  # Figure 5 for page 3 (Center bottom)
    
    # Figure 6 (Line Chart)
    dcc.Graph(id='time-series-plot-page-3', config={'displaylogo': False, 'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomOut2d']}),  # Figure 6 for page 3
])

# Create the Dash app layout
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-page-1', children=[
        dcc.Tab(label='Page 1', value='tab-page-1'),
        dcc.Tab(label='Page 2', value='tab-page-2'),
        dcc.Tab(label='Page 3', value='tab-page-3'),
    ]),
    html.Div(id='tabs-content')
])

# Callback to display the selected page layout based on tabs
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def display_tab_content(selected_tab):
    if selected_tab == 'tab-page-1':
        return page_1_layout
    elif selected_tab == 'tab-page-2':
        return page_2_layout
    elif selected_tab == 'tab-page-3':
        return page_3_layout

# Callbacks for updating figures based on user input in page 1
@app.callback(
    Output('graph-content1-page-1', 'figure'),
    Output('graph-content2-page-1', 'figure'),
    Input('dropdown-selection-page-1', 'value'),
    Input('interval-selection-page-1', 'value'),
)
def update_graph_page_1(selected_shift_page_1, interval_page_1):
    fig1 = create_figure1(selected_shift_page_1)
    fig2 = create_figure2(selected_shift_page_1, interval_page_1)
    return fig1, fig2

# Callbacks for updating figures based on user input in page 2
@app.callback(
    Output('graph-content3-page-2', 'figure'),
    Output('graph-content4-page-2', 'figure'),
    Input('dropdown-selection-page-2', 'value')
)
def update_graph_page_2(selected_shift_page_2):
    fig3 = create_figure3(selected_shift_page_2)
    fig4 = create_figure4(selected_shift_page_2)
    return fig3, fig4

# Callback for updating the Power Consumption Pie Chart in page 3
@app.callback(
    Output('power-pie-chart-page-3', 'figure'),
    Output('time-series-plot-page-3', 'figure'),
    Input('tabs', 'value')  # Added tabs value as an input to decide which figure to display in page 3
)
def update_page_3_content(selected_tab):
    if selected_tab == 'tab-page-3':
        fig6 = create_figure5('Overall')  # For Figure 5
        fig5 = create_figure6()  # For Figure 6
        return fig5, fig6
    return {}, {}  # Return empty figures if not on page 3

if __name__ == '__main__':
    app.run_server(debug=True)
