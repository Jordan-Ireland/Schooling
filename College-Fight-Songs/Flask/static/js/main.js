var index = 0;
var plot = document.getElementById('chart');
var schoolInfo;
var data;
var customPlot = document.getElementById('custom_chart')
var customPlot2 = document.getElementById('custom-chart2')
var loadingIcon = $('#loading')
var loaded = false
var loadingBar = $('#progress-bar')

var token = 'MY_SPOTIFY_TOKEN'

var audioSource = $('#audio-source'),
    audioController = $('#audio-cont')

var tropes = ['fight', 'victory', 'win_won', 'rah', 'nonsense', 'colors', 'men', 'opponents', 'spelling']

function UpdateSchool(ind, hasTrace = false) {
    $('#school').attr('disabled', true)
    loadingIcon.removeClass('hide')
    $('#custom_chart').attr('hidden', true)

    index = ind

    GetAudioTrack()

    $('#school').val(index);
    if (hasTrace == true) {
        Plotly.deleteTraces(plot, 0)
    }
    Plotly.addTraces(plot, {
        y: [schoolInfo['danceability'][index]], x: [schoolInfo['sec_duration'][index]], type: 'scatter', mode: 'markers',
        marker: { size:15, color: 'rgb(0,0, 255)', opacity: 1}, hoverinfo:'none'
    }, 0)

    for (var key in schoolInfo) {
        if (jQuery.inArray(key.toString(), tropes) > -1) {
            //schoolInfo[key][index] == 1 ? $('#' + key.toString()).prop("checked", true) : $('#' + key.toString()).prop("checked", false)
            if (!$('#' + key.toString()).hasClass("checked")) {
                if (schoolInfo[key][index] == 1)
                    $('#' + key.toString()).addClass("checked");
            } else if ($('#' + key.toString()).hasClass("checked")) {
                if (schoolInfo[key][index] == 0)
                    $('#' + key.toString()).removeClass("checked");
            }
        }
    }
    $('#fight-times').innerHTML = schoolInfo['number_fights'][index]

    SongAnalysis()
}

function SongAnalysis() {
    $.ajax({
        type: "POST",
        url: "/custom_analysis/",
        data: JSON.stringify({ 'index': index }),
        contentType: "application/json",
        dataType: "json",
        success: function (data) {
            loadingIcon.addClass('hide')
            $('#custom_chart').attr('hidden', false)

            Plotly.newPlot(customPlot, data['traces'], data['layout'], {
                responsive: true, dragmode: false,
                modeBarButtonsToRemove: ['zoom2d', 'pan2d', 'lasso2d',
                    'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d', 'select2d']
            })
            
            Plotly.newPlot(customPlot2, data['customTrace2'], data['customLayout2'], {
                responsive: true, dragmode: false,
                modeBarButtonsToRemove: ['zoom2d', 'pan2d', 'lasso2d',
                    'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d', 'select2d']
            })
            loaded = true
            $('#school').attr('disabled', false)

            $('#song-analysis').html(data['analysis'])
        },
        failure: function (errMsg) {
            alert(errMsg);
        }
    });

    $('#totalTropes').text("Total Tropes: " + schoolInfo['trope_count'][index])

    $('.gtitle').text(schoolInfo['school'][index] + ' -- ' + schoolInfo['song_name'][index])
}

function TestFunction(json_data) {
    JSON.parse(json_data)

    Plotly.newPlot(customPlot, json_data['traces'], json_data['layout'], {
                responsive: true, dragmode: false,
                modeBarButtonsToRemove: ['zoom2d', 'pan2d', 'lasso2d',
                    'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d', 'select2d']
            })
}

function isPlaying(audio) {
    loadingBar.css('width', audio.currentTime / audio.duration * 100 + '%')
}

function AudioControls(playing = false) {
    switch (playing) {
        case true:
            $('#play').addClass('hidden')
            $('#pause').removeClass('hidden')

            audioController[0].play()
            break;
        case false:
            $('#pause').addClass('hidden')
            $('#play').removeClass('hidden')

            audioController[0].pause()
            break;
    }
}

$.get("/get_chart", function (chart_data) {
    $('#pageLoader').addClass('hide')
    data = JSON.parse(chart_data)
    schoolInfo = data['pandas']
    LoadChart()
    AddOptions()
});

function LoadChart() {
    audioController.on('ended', function () {
        AudioControls(false)
    });

    Plotly.newPlot(plot, data['traces'], data['layout'], {
        responsive: true, dragmode: false,
        modeBarButtonsToRemove: ['zoom2d', 'pan2d', 'lasso2d',
            'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d', 'select2d']
    })

    plot.on('plotly_click', function (clickData) {
        if (loaded === true) {
            if(index != clickData['points'][0]['pointIndex']) {
                UpdateSchool(clickData['points'][0]['pointIndex'], true)
                loaded = false
            }
        } 
    })
    UpdateSchool(0)
}

function AddOptions() {
    var selector = document.getElementById('school');
    for (var key in schoolInfo['school']) {
        selector.innerHTML += '<option value="' + key + '">' + schoolInfo['school'][key] + ' -- ' + schoolInfo['song_name'][key] + '</option>'
    }
}

function GetAudioTrack() {
    if (Date.now() > parseInt(getCookie('expires_at')) || getCookie('expires_at') == null)
        GetOAuth(true)
    else {
        AudioControls(false)
        $.ajax({
            url: 'https://api.spotify.com/v1/tracks/' + schoolInfo['spotify_id'][index],
            dataType: 'JSON',
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', 'Bearer ' + String(getCookie('access_token')));
            },
            success: function (response) {
                //console.log(response)
                $('.audio').css('background-color', schoolInfo['color_code'][index])
                loadingBar.css('width', '0%')
                audioSource.attr('src', response['preview_url'])
                audioController[0].pause()
                audioController[0].load()
            },
            failure: function (errMsg) {
                alert(errMsg);
            }
        });
    }
}

function GetOAuth(gettingAudio = false) {
    $.ajax({
        url: 'https://accounts.spotify.com/api/token',
        type: 'POST',
        dataType: 'JSON',
        contentType: 'application/x-www-form-urlencoded',
        beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'Basic ' + token);
        },
        data: {
            'grant_type':'client_credentials'
        },
        success: function (response) {
            //console.log(response)

            setCookie('access_token', String(response['access_token']), response['expires_in'])
            setCookie('token_type', String(response['token_type']), response['expires_in'])
            setCookie('expires_at', String((response['expires_in'] * 60) + Date.now()), response['expires_in'])

            if (gettingAudio)
                GetAudioTrack();
        },
        failure: function (errMsg) {
            alert(errMsg);
        }
    });    
}

function setCookie(key, value, expiry) {
    var expires = new Date();
    expires.setTime(expires.getTime() + (expiry * 60));
    document.cookie = key + '=' + value + ';expires=' + expires.toUTCString();
}

function getCookie(key) {
    var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
    return keyValue ? keyValue[2] : null;
}

function eraseCookie(key) {
    var keyValue = getCookie(key);
    setCookie(key, keyValue, '-1');
}