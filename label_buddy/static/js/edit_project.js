// if redirect after project has no labels clear url
document.addEventListener('DOMContentLoaded', function() {
    var url = window.location.href;
    parameters = url.split('?')[1]
    if(parameters) {
        document.getElementById('new_labels').style.border = '1px solid red'
        window.history.pushState({}, '', "/projects/" + project_id + "/edit");
    }
});