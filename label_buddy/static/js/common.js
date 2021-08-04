$(document).ready(function(){
    $('.clickable-row').click(function(){
        window.location = $(this).attr('href');
        return false;
    });
});