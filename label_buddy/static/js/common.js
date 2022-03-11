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

document.addEventListener('DOMContentLoaded', function() {
    $('.tooltip-icons').data('title'); // "This is a test";

    $(function () {
        $('[data-toggle="tooltip"]').tooltip({
            trigger : 'hover'
        })
    });

    $('form').on('submit',function(){
        NProgress.start();
    });
});
