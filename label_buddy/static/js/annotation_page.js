var selected_label = null;
var selected_label_color = null;
var selected_region = null;
var initial_opacity = .4;
var selected_region_opacity = .9;
var wavesurfer; // eslint-disable-line no-var

function toggleIcon(button){
    $(button).find('i').remove();
    if (wavesurfer.backend.isPaused()) {
        $(button).html($('<i/>',{class:'fas fa-play'})).append(' Play');
    }
    else {
        $(button).html($('<i/>',{class:'fas fa-pause'})).append(' Pause');
    }
}

function selectedLabel(button) {

    if(selected_label == button) {
        selected_label.style.border = 'none';
        selected_label.style.background = selected_label_color;
        selected_label = null;
        selected_label_color = null;
        // if no label is selected user cannot drag
        wavesurfer.disableDragSelection();
    } else {
        // if label already selected, unselect it
        if(selected_label) {
            selected_label.style.border = 'none';
            selected_label.style.background = selected_label_color;
        }

        // set new selected label
        selected_label = button;
        selected_label_color = button.style.backgroundColor;
        
        // enable drag selection with label's color
        wavesurfer.enableDragSelection({
            color: rgbToRgba(selected_label_color, initial_opacity)
        });
        button.style.border = '2px solid #74deed';
        button.style.background = 'grey'
    }
}

// rgb to rgba with opacity 0.1
function rgbToRgba(rgb, opacity) {
    if(rgb.indexOf('a') == -1){
        var rgba = rgb.replace(')', ', ' + opacity + ')').replace('rgb', 'rgba');
    }
    return rgba;
}
//----------------------------------------------------------------------------------------------



document.addEventListener('DOMContentLoaded', function() {
    // Init wavesurfer
    wavesurfer = WaveSurfer.create({
        container: '#waveform',
        height: 150,
        pixelRatio: 1,
        scrollParent: true,
        normalize: true,
        minimap: true,
        splitChannels: true,
        waveColor: '#ddd',
        progressColor: '#74deed',
        backend: 'MediaElement',
        plugins: [
            WaveSurfer.regions.create(),
            WaveSurfer.minimap.create({
                height: 30,
                waveColor: '#ddd',
                progressColor: '#74deed',
                cursorColor: '#999'
            }),
            WaveSurfer.timeline.create({
                container: '#wave-timeline'
            }),
            WaveSurfer.cursor.create({
                showTime: true,
                opacity: 1,
                customShowTimeStyle: {
                    'background-color': '#000',
                    color: '#fff',
                    padding: '2px',
                    'font-size': '10px'
                }
            }),
        ]
    });
    wavesurfer.load(audio_url);

    /* Regions */

    // load regions of existing annotation (if exists)
    wavesurfer.on('ready', function() {
        result = annotation['result']
        // if there is a result load regions of annotation
        if(result && result.length != 0) {
            loadRegions(result);
        }
    });

    
    // on region click
    wavesurfer.on('region-click', function(region) {
        console.log("remove");
        region.remove();

        // if region already selected, unselect it
        if(selected_region == region) {
            region.color = rgbToRgba(region.data['color'], initial_opacity);
            region.data['from-click'] = true;
            selected_region = null;
            wavesurfer.addRegion(region);
            //document.getElementById('delete-region-btn').style.visibility = 'hidden';
            document.getElementById('delete-region-btn').disabled = true;
        } else {

            // if another region is selected, unselect it
            if(selected_region) {
                selected_region.remove();
                selected_region.color = rgbToRgba(selected_region.data['color'], initial_opacity);
                selected_region.data['from-click'] = true;
                wavesurfer.addRegion(selected_region);
            }
            
            region.color = rgbToRgba(region.data['color'], selected_region_opacity);
            region.data['from-click'] = true;
            selected_region = wavesurfer.addRegion(region);
            //document.getElementById('delete-region-btn').style.visibility = 'visible';
            document.getElementById('delete-region-btn').disabled = false;
        }
    });


    // on region created set its data to current label
    wavesurfer.on('region-created', function(region) {
        if(selected_label && !region.data['from-click']) {
            region.data['label'] = selected_label.value;
            region.data['color'] = selected_label_color;
        }
    });

    // play regions on double click
    // wavesurfer.on('region-dblclick', function(region, e) {
    //     console.log("play");
    //     if(selected_region)
    //         wavesurfer.play(selected_region.start);
    //     // e.stopPropagation();
    //     // // Play on click, loop on shift click
    //     // e.shiftKey ? region.playLoop() : wavesurfer.play(region.start);
    // });
    
    // // when region plays, take audio to the beggining of the region
    // wavesurfer.on('region-play', function(region) {
    //     region.once('out', function() {
    //         wavesurfer.play(region.start);
    //         wavesurfer.pause();
    //     });
    // });

});


function createResult() {
    // annotation result will be an array of dictionaries
    // each dict will represent a region
    let result = [];
    Object.keys(wavesurfer.regions.list).map(function(id) {
        let region = wavesurfer.regions.list[id];
        let region_dict = {
            "audio_length": wavesurfer.getDuration(),
            "value": {
                "start": region.start,
                "end": region.end,
                "label": region.data['label'],
                "color": region.data['color']
            }
        }
        result.push(region_dict);
    })
    return result;
}

function submitAnnotation() {
    // xmlhttp request for saving the annotation
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // Typical action to be performed when the document is ready:
            const response = JSON.parse(this.responseText);
            alert(response['message']);
        } else if(this.readyState == 4 && (this.status == 400 || this.status == 401)){
            const response = JSON.parse(this.responseText);
            alert(response['message']);
        }
    };
    let url = "http://127.0.0.1:8000/api/v1/projects/" + project_id + "/tasks/" + task_id + "/annotation/save";
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader("X-CSRFToken", django_csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(createResult()));
}

// Load regions from annotation.
function loadRegions(result) {
    for(const region of result) {
        let new_region = wavesurfer.addRegion({
            "start": region['value']['start'],
            "end": region['value']['end'],
            "color": rgbToRgba(region['value']['color'], initial_opacity)
        });
        new_region.data['label'] = region['value']['label'];
        new_region.data['color'] = region['value']['color'];
    }
}

// remove region
function removeRegion(button) {
    if(selected_region){
        selected_region.remove();
        selected_region = null;
        button.disabled = true;
    }
}

// backwardAudio audio to start
function backwardAudio() {
    wavesurfer.stop();
    toggleIcon(document.getElementById('play-pause-button'));
}

document.getElementById('zoom-slider').oninput = function () {
    wavesurfer.zoom(Number(this.value));
};