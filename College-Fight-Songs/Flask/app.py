from flask import Flask, render_template, url_for, request
import json
import plotly.graph_objects as go
import plotly.utils as pu

app = Flask(__name__)

with open('fight-songs.json', encoding="utf8") as f:
    df = json.load(f)
with open('fight-songs-normalized.json', encoding="utf8") as f:
    norm_df = json.load(f)
with open('averages.json', encoding="utf-8") as f:
    avgs = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

def create_analysis(index):
    index = str(index)
    time = float(avgs["duration"]) - df["sec_duration"][index]
    color_box = '<span class="color-box" style="background-color:{}"></span>'.format(df["color_code"][index])
    
    text = '{} was written in {} by '.format(df["song_name"][index],df["year"][index]) + \
    '{}'.format("students: " + df["new_writers"][index] if df["student_writer"][index] == "1" else df["new_writers"][index] ) + \
    '{} It is currently {}\'s '.format( " as part of a contest." if df["contest"][index] == 1 else "." ,df["school"][index]) + \
    '{} song. <br />The song has a <strong>Tempo</strong> (beats per minute) of '.format( "official" if df["official_song"][index] == 1 else "unofficial") + \
    '{}, which is {} than the average '.format( df["tempo"][index] , "higher" if float(avgs["tempo"]) < df["tempo"][index] else "lower" ) + \
    'tempo. It has {} tropes, average is {}. It is '.format( df["trope_count"][index] , avgs["trope_count"] ) + \
    '<strong>{}</strong>'.format( ("slightly longer" if time + 20 >= 0 else "much longer") if time < 0 else ("slightly shorter" if time - 20 <= 0 else "much shorter") ) + \
    ' than the average length of a fight song. {}\'s main official color is <strong>{}</strong><br />'.format(df["school"][index],df["color_code"][index] + " " + color_box) + \
    'All but 1 fight song is in 4/4 time (how many beats per measure).<br /><br />'
    
    traces, layout = custom_chart2(index)
    
    return text, traces, layout
    
def custom_chart2(index):
    index = str(index)
    notfeatures=['tempo','trope_count','number_fights','duration','loudness']
    x,y,y2=[],[],[]
    for key in avgs.keys():
        if key not in notfeatures:
            x.append(key)
            y.append(avgs[key])
            y2.append(df[key][index])

    traces = [go.Bar(name='Average', 
                     x=x, 
                     y=y,
                     hoverinfo='none',
                     hovertemplate=
                     '<b>%{text}:</b> %{y}<br>' +
                     '<extra></extra>',
                     text = ['Average'] * len(x),
                     showlegend=False,
                     marker=dict(color='rgb(220,220,220)')),
              go.Bar(name=df['school'][index],
                     x=x,
                     y=y2,
                     hoverinfo='none',
                     hovertemplate=
                     '<b>%{text}:</b> %{y}<br>' +
                     '<extra></extra>',
                     text = [df["school"][index]] * len(x),
                     showlegend=False,
                     marker=dict(color=df['color_code'][index]))]
    layout = go.Layout(barmode='group',
                      xaxis=dict(fixedrange=True),
                      yaxis=dict(fixedrange=True))
    
    return traces, layout

@app.route('/custom_analysis/', methods=["POST"])
def custom_analysis():
    data = request.get_json()
    index = data['index']
    analysis, trace2, layout2 = create_analysis(index)
    features = ['sec_duration', 'danceability', 'energy', 'loudness',
                'valence', 'tempo', 'sec_duration']
    r = []
    for key in features:
        r.append(norm_df[int(index)][str(key)])
    trace = [go.Scatterpolar(
        r=r,
        theta=['Duration', 'Danceablity', 'Energy', 'Loudness',
               'Valence', 'Tempo', 'Duration'],
        fill='toself',
        fillcolor=df['color_code'][str(index)],
        line=dict(color='rgb(0,0,0)', width=2),
        connectgaps=True,
        hoveron='points',
        opacity=1,
        hoverinfo='none',
        hovertemplate=
        '<b>%{theta}:</b> %{r}<br>' +
        '<extra></extra>',
        hoverlabel=dict(bgcolor='rgb(255,255,255)')
    )]
    layout = go.Layout(
        polar=dict(radialaxis=dict(
                visible=True,
                type='linear',
                nticks=3,
                range=[0, 1]),
            ),
            showlegend=False,
            autosize=True,
            margin=dict(l=0,r=0,t=25,b=25,pad=2),
            height=250
    )

    return json.dumps(
        {'traces': trace, 'layout': layout, 'analysis': analysis, 'customTrace2': trace2, 'customLayout2': layout2 },
        cls=pu.PlotlyJSONEncoder)


@app.route('/get_chart')
def create_figure():
    #import pandas as pd

    #df = pd.read_csv('new-fight-songs.csv')



    traces = [go.Scatter(
        x=[df['sec_duration'][str(i)] for i in range(len(df['sec_duration']))],
        y=[df['danceability'][str(i)] for i in range(len(df['danceability']))],
        mode='markers',
        hoverinfo='none',
        hovertemplate=
        '%{text}' +
        '<b>Duration:</b> %{x}<br>' +
        '<b>Danceability:</b> %{y}<br>' +
        '<extra></extra>',
        # hoverlabel=dict(bgcolor='rgb(255,255,255)'),
        text=[
            '<b>School:</b> {}<br><b>Song Title:</b> {}<br><b>Trope '
            'Count:</b> {}<br>'.format(
                df['school'][str(i)], df['song_name'][str(i)], df['trope_count'][str(i)]) for i
            in range(len(df['school']))],
        marker=dict(size=15, color=[df['color_code'][str(i)] for i in range(len(df['color_code']))], opacity=0.3),
        showlegend=False
    ), go.Scatter(
        x=[0, 180],
        y=[avgs['danceability']],
        mode="lines",
        line=go.scatter.Line(color="gray"),
        hoverinfo='none',
        showlegend=False
    ), go.Scatter(
        y=[0, 1],
        x=[avgs['duration'], avgs['duration']],
        mode="lines",
        line=go.scatter.Line(color="gray"),
        hoverinfo='none',
        showlegend=False)
    ]

    layout = go.Layout(
        title='SCHOOL NAME -- SONG NAME',
        xaxis_title="Duration",
        yaxis_title="Danceability",
        font=dict(
            size=15,
            color="#7f7f7f"
        ),
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        plot_bgcolor='rgb(255,255,255)',
        showlegend=False,
        hovermode='closest',
        autosize=True,
        dragmode=False,
        annotations=[
            dict(
                x=0.1,
                y=0.95,
                xref="paper",
                yref="paper",
                text="Short and Danceable",
                showarrow=False
            ),
            dict(
                x=0.9,
                y=0.95,
                xref="paper",
                yref="paper",
                text="Long and Jiggy",
                showarrow=False
            ),
            dict(
                x=0.1,
                y=0.05,
                xref="paper",
                yref="paper",
                text="Short and Mellow",
                showarrow=False
            ),
            dict(
                x=0.9,
                y=0.05,
                xref="paper",
                yref="paper",
                text="Long and Boring",
                showarrow=False
            )
        ],
        xaxis=dict(fixedrange=True, range=[0, 180]),
        yaxis=dict(fixedrange=True, range=[0.2, 0.9])
    )

    return json.dumps(
        {'traces': traces, 'layout': layout, 'pandas': df},
        cls=pu.PlotlyJSONEncoder)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')
