// var wavesurfer = WaveSurfer.create({
//     container: null
// });

// wavesurfer.load('http://ia902606.us.archive.org/35/items/shortpoetry_047_librivox/song_cjrg_teasdale_64kb.mp3');

// wavesurfer.on('ready', function () {
//     wavesurfer.play();
// });

function filter_tasks() {
    var url = window.location.href;
    url = url.split('?')[0]
    
    var labeled = document.getElementById("labeled").checked;
    var unlabeled = document.getElementById("unlabeled").checked;
    var reviewed = document.getElementById("reviewed").checked;
    var unreviewed = document.getElementById("unreviewed").checked;

   
    // check if both are checked then uncheck them
    if(labeled && unlabeled) {
        labeled = false;
        unlabeled = false;
    }

    if(reviewed && unreviewed) {
        reviewed = false;
        unreviewed = false;
    }

    // url here has no parameters
    if(labeled)
        url += '?labeled=true';

    if(unlabeled)
        url += '?labeled=false';

    if(reviewed) {
        if (url.indexOf('?') > -1) {
            url += '&reviewed=true'
        } else{
            url += '?reviewed=true'
        }
    }

    if(unreviewed) {
        if (url.indexOf('?') > -1) {
            url += '&reviewed=false'
        } else{
            url += '?reviewed=false'
        }
    }
    window.location.href = url;
}

