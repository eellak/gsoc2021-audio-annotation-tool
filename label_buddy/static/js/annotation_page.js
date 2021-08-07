var selected_label = null;
var selected_label_color = null;
var selected_region = null;
var selected_region_button = null;
var regions_count = 0;
var color_when_selected = '#74deed';
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
        // selected_label.style.border = '2px solid ' + selected_label_color;
        selected_label.style.opacity = initial_opacity;
        //selected_label.style.background = selected_label_color;
        selected_label = null;
        selected_label_color = null;
        // if no label is selected user cannot drag
        wavesurfer.disableDragSelection();
    } else {
        // if label already selected, unselect it
        if(selected_label) {
            selected_label.style.opacity = initial_opacity;
        }

        // set new selected label
        selected_label = button;
        selected_label_color = button.style.backgroundColor;
        
        // enable drag selection with label's color
        wavesurfer.enableDragSelection({
            color: rgbToRgba(selected_label_color, initial_opacity)
        });
        selected_label.style.opacity = 1;
    }
}

function selectRegionButton(button) {
    let region_by_id = wavesurfer.regions.list[button.id];
    if(selected_region_button == button) {
        selected_region_button.style.opacity = initial_opacity;
        selected_region_button.style.fontWeight = 'normal';
        selected_region_button.style.backgroundColor = 'rgb(245,245,245)'
        selected_region_button = null;

        // if region selected, unselect it
        if(selected_region == region_by_id) {
            region_by_id.wavesurfer.fireEvent('region-click', region_by_id);
        }
    } else {
        // if label already selected, unselect it
        if(selected_region_button) {
            
            selected_region_button.style.opacity = initial_opacity;
            selected_region_button.style.fontWeight = 'normal';
            selected_region_button.style.backgroundColor = 'rgb(245,245,245)';
            // if region selected, unselect it
            if(selected_region == region_by_id) {
                region_by_id.wavesurfer.fireEvent('region-click', region_by_id);
            }
        }
        
        selected_region_button = button;
        selected_region_button.style.opacity = selected_region_opacity;
        selected_region_button.style.backgroundColor = '#dddddd';
        selected_region_button.style.fontWeight = 'bold';

        if(selected_region != region_by_id) {
            region_by_id.wavesurfer.fireEvent('region-click', region_by_id);
        }
    }

}

function hoverRegionButtonIn(button) {
    button.style.opacity = selected_region_opacity;
    button.style.backgroundColor = '#dddddd';
    let region_by_id = wavesurfer.regions.list[button.id];
    region_by_id.update({
        color: rgbToRgba(region_by_id.data['color'], selected_region_opacity)
    });
    getLabelButton(region_by_id.data['label']).style.opacity = selected_region_opacity;
}

function hoverRegionButtonOut(button) {
    let region_by_id = wavesurfer.regions.list[button.id];
    if(selected_region_button != button) {
        button.style.opacity = initial_opacity;
        button.style.backgroundColor = 'rgb(245,245,245)';
        region_by_id.update({
            color: rgbToRgba(region_by_id.data['color'], initial_opacity)
        });
    }

    let lbl_button = getLabelButton(region_by_id.data['label']);
    if(selected_label != lbl_button) {
        lbl_button.style.opacity = initial_opacity;
    }
}

// rgb to rgba with opacity 0.1
function rgbToRgba(rgb, opacity) {
    if(rgb.indexOf('a') == -1){
        var rgba = rgb.replace(')', ', ' + opacity + ')').replace('rgb', 'rgba');
    }
    return rgba;
}

// get label to select after region click
function getLabelButton(label) {
    var alllabels = document.getElementsByClassName('my-badge');
    for(const x of alllabels) {
        if(x.value == label) {
            return x;
        }
    }
}

function getLabelColorByValue(label)
{
    var alllabels = document.getElementsByClassName('my-badge');
    for(const x of alllabels) {
        if(x.value == label) {
            return x.style.backgroundColor;
        }
    }
}

function showAlert() {
    location.reload(true);
}

function getRegionButton(new_region) {
    let new_region_button = document.createElement('BUTTON');
    // set attributes
    new_region_button.className = 'region-buttons';
    // new_region_button.style.backgroundColor = new_region.data['color'];
    new_region_button.style.opacity = initial_opacity;
    new_region_button.id = new_region.id;
    new_region_button.title = "Label: " + new_region.data['label'];

    new_region_button.setAttribute( "onClick", "selectRegionButton(this);" );
    new_region_button.setAttribute( "onmouseover", "hoverRegionButtonIn(this);" );
    new_region_button.setAttribute( "onmouseout", "hoverRegionButtonOut(this);" );

    let count = document.createElement("SPAN");
    count.id = "count";
    count.style.display = 'inline-block';
    count.style.width = '35px'
    count.style.marginRight = '7px'
    
    let icon = document.createElement('i');
    icon.className = 'fas fa-music';
    icon.style.marginRight = "10px";
    icon.style.color = new_region.data['color'];

    let timings = document.createElement("SPAN");
    timings.id = "timings";

    count.textContent = regions_count + ".";
    timings.textContent = (Math.round((new_region.start + Number.EPSILON) * 100) / 100) + " - " + (Math.round((new_region.end + Number.EPSILON) * 100) / 100);
    new_region_button.appendChild(count);
    new_region_button.appendChild(icon);
    new_region_button.appendChild(timings);
    return new_region_button;
}

function add_region_to_section(region) {
    // load region to region section
    let new_region_button = getRegionButton(region);
    $('#regions-div').append(new_region_button);
}

function fixNumberOfRegions() {
    let counter = 1;
    region_buttons = document.getElementsByClassName('region-buttons');
    for(btn of region_buttons) {
        $(btn).find('#count').text(counter++ + ".")
    }
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
                    'font-size': '15px'
                }
            }),
        ]
    });
    wavesurfer.load(audio_url);

    /* Regions */

    // load regions of existing annotation (if exists)
    wavesurfer.on('ready', function() {
        wavesurfer.setPlaybackRate(1);
        wavesurfer.zoom(0); // initial zoom
        wavesurfer.setVolume(1); // initial volume
        let result = annotation
        // if there is a result load regions of annotation
        if(result && result.length != 0) {
            loadRegions(result);
        } else {
            document.getElementById('delete-annotation-btn').disabled = 'true';
        }
    });


    // on region click select it
    wavesurfer.on('region-click', function(region) {
        let region_button = document.getElementById(region.id);

        // if region already selected, unselect it
        if(selected_region == region) {
            region.update({
                color: rgbToRgba(region.data['color'], initial_opacity)
            });
            selected_region = null;
            document.getElementById('delete-region-btn').style.display = 'none';
            document.getElementById('play-region-btn').style.display = 'none';

            // deactivate label of region
            let lbl = getLabelButton(region.data['label']);
            if(selected_label == lbl) lbl.click();

            // deactivate region button
            if(selected_region_button == region_button) {
                region_button.click();
            }

        } else {

            // if another region is selected, unselect it
            if(selected_region) {
                selected_region.update({
                    color: rgbToRgba(selected_region.data['color'], initial_opacity)
                });

                // deactivate label of region
                let lbl = getLabelButton(selected_region.data['label']);
                if(selected_label == lbl) lbl.click();

                // deactivate region button
                if(selected_region_button == region_button) {
                    region_button.click();
                }
            }

            region.update({
                color: rgbToRgba(region.data['color'], selected_region_opacity)
            });
            selected_region = region;
            document.getElementById('delete-region-btn').style.display = 'inline';
            document.getElementById('play-region-btn').style.display = 'inline';

            // activate label of region
            let lbl = getLabelButton(region.data['label']);
            if(selected_label != lbl) lbl.click();

            // activate region button
            if(selected_region_button != region_button) {
                region_button.click();
            }
        }
    });


    // on region created set its data to current label
    wavesurfer.on('region-created', function(region) {
        // increase counter
        if(++regions_count == 1) {
            document.getElementById('remove_all_regions').style.display = 'block';
        }
        if(selected_label) {
            region.data['label'] = selected_label.value;
            region.data['color'] = selected_label_color;
        } else {
            add_region_to_section(region);
        }
    });

    // on region created set its data to current label
    wavesurfer.on('region-update-end', function(region) {
        let region_button = document.getElementById(region.id);
        if(!document.getElementById(region.id)) {
            // if region does not exists, add it
            add_region_to_section(region);
        } else {
            // else update it
            $("#" + region.id).find('#timings').text(
                (Math.round((region.start + Number.EPSILON) * 100) / 100) + " - " + (Math.round((region.end + Number.EPSILON) * 100) / 100)
                );
        }
    });

    // when region plays, take audio to the beggining of the region
    wavesurfer.on('region-update-end', function(region) {
        region.once('out', function() {
            wavesurfer.pause();
            toggleIcon(document.getElementById('play-pause-button'));
        });
    });

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
            showAlert(response['message'], this.status);
        } else if(this.readyState == 4 && (this.status == 400 || this.status == 401)){
            const response = JSON.parse(this.responseText);
            showAlert(response['message'], this.status);
        }
    };
    let url = host + "api/v1/projects/" + project_id + "/tasks/" + task_id + "/annotation/save";
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader("X-CSRFToken", django_csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(createResult()));
}

// Load regions from annotation.
function loadRegions(result) {
    for(const region of result) {
        wavesurfer.addRegion({
            start: region['value']['start'],
            end: region['value']['end'],
            color: rgbToRgba(getLabelColorByValue(region['value']['label']), initial_opacity),
            data: {
                label: region['value']['label'],
                color: getLabelColorByValue(region['value']['label'])
            }
        });
    }
}

// delete region link
$('#delete-region-btn').click( function(e) {
    e.preventDefault(); 
    if(selected_region){

        // if label is selected, unselect it
        let lbl = getLabelButton(selected_region.data['label'])
        if(selected_label == lbl) lbl.click();

        // delete region button
        let region_button = document.getElementById(selected_region.id);
        region_button.remove();

        selected_region.remove();
        fixNumberOfRegions();
        // decrease counter
        if(--regions_count == 0) {
            document.getElementById('remove_all_regions').style.display = 'none';
        }
        selected_region = null;
        document.getElementById('delete-region-btn').style.display = 'none';
        document.getElementById('play-region-btn').style.display = 'none';
    }
    return false; 
} );

// play region link
$('#play-region-btn').click( function(e) {
    e.preventDefault(); 
    if(selected_region){
        selected_region.play();
        toggleIcon(document.getElementById('play-pause-button'));
    }
    return false; 
} );

// backwardAudio audio to start
function backwardAudio() {
    wavesurfer.stop();
    toggleIcon(document.getElementById('play-pause-button'));
}

document.getElementById('zoom-slider').oninput = function () {
    wavesurfer.zoom(Number(this.value));
};

function toggleSoundIcon(slider){
    wavesurfer.setVolume(Number(slider.value));
    let sound_slider_icon = document.getElementById('sound-slider-icon');
    if(slider.value > 0 && slider.value <= .5) {
        sound_slider_icon.classList.toggle('fa-volume-down');
    } else if(slider.value > .5){
        sound_slider_icon.classList.toggle('fa-volume-up');
    } else {
        sound_slider_icon.classList.toggle('fa-volume-mute');
    }
};

// mute unmute button
$('#mute-unmute-btn').click( function(e) {
    e.preventDefault(); 
    let current_volume = wavesurfer.getVolume();
    let sound_slider = document.getElementById('sound-slider');
    if(current_volume > 0) {
        // then mute
        sound_slider.value = 0;
        toggleSoundIcon(sound_slider);
    } else {
        sound_slider.value = .5;
        toggleSoundIcon(sound_slider);
    }
    return false; 
} );


function changeSpeed(selector) {
    wavesurfer.setPlaybackRate(selector.value);
}

// remove all regions button
$('#remove_all_regions').click( function(e) {
    e.preventDefault(); 
    Object.keys(wavesurfer.regions.list).forEach(function (id) {
        let region = wavesurfer.regions.list[id];
        let region_button = document.getElementById(region.id);

        // if label is selected, unselect it
        region.remove();
        region_button.remove();
        // set counter to 0
        regions_count = 0;
        selected_region = null;
        selected_region_button = null;
        document.getElementById('remove_all_regions').style.display = 'none';
        document.getElementById('delete-region-btn').style.display = 'none';
        document.getElementById('play-region-btn').style.display = 'none';
    });
    return false; 
} );
