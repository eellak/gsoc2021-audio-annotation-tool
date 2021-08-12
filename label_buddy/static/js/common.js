$(document).ready(function(){
    $('.clickable-row').click(function(){
        window.location = $(this).attr('href');
        return false;
    });
});

$(window).load(function(){
    NProgress.done();
 });
 
 $(document).ready(function() {
    NProgress.start();
 });