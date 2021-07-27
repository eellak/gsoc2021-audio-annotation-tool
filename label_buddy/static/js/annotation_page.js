var wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: 'rgb(245,245,245)',
    progressColor: '#74deed'
});

wavesurfer.load(audio_url);

// wavesurfer.on('ready', function () {
//     wavesurfer.play();
// });

function toggleIcon(button){
    $(button).find('i').remove();
    if (wavesurfer.backend.isPaused()) {
        $(button).html($('<i/>',{class:'fas fa-play'})).append(' Play');
    }
    else {
        $(button).html($('<i/>',{class:'fas fa-pause'})).append(' Pause');
    }
}