$(document).ready(function(){
    fixFilters();
});


// fix filters after page reload
function fixFilters() {
    var parameters = window.location.href.split('?')[1];
    if(parameters) {
        for(let param of parameters.split('&')) {
            name = param.split('=')[0];
            value = param.split('=')[1].toLowerCase();

            if(name == 'approved') {
                if(value == 'true') {
                    document.getElementById("approved").checked = true;
                } 
            } else if(name == 'rejected') {
                if(value == 'true') {
                    document.getElementById("rejected").checked = true;
                }
            } else if(name == 'unreviewed') {
                if(value == 'true') {
                    document.getElementById("unreviewed").checked = true;
                }
            }
        }
    }

}

// filter annotations on list_annotations page
function filter_tasks() {
    var url = window.location.href;
    url = url.split('?')[0]
    var approved = document.getElementById("approved").checked;
    var rejected = document.getElementById("rejected").checked;
    var unreviewed = document.getElementById("unreviewed").checked;

   
    // check if all are checked then uncheck them
    if(approved && rejected && unreviewed) {
        // select all annotations
        // just reload
    } else {
        // url here has no parameters
        if(approved)
            url += '?approved=true';
        
        if(rejected) {
            if (url.indexOf('?') > -1) {
                url += '&rejected=true'
            } else{
                url += '?rejected=true'
            }
        }

        if(unreviewed) {
            if (url.indexOf('?') > -1) {
                url += '&unreviewed=true'
            } else{
                url += '?unreviewed=true'
            }
        }
    }
    window.location.href = url;
}