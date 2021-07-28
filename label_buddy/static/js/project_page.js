// fix filters after page reload
function fixFilters() {
    var parameters = window.location.href.split('?')[1];
    if(parameters) {
        for(let param of parameters.split('&')) {
            name = param.split('=')[0];
            value = param.split('=')[1].toLowerCase();

            if(name == 'labeled') {
                if(value == 'true') {
                    document.getElementById("labeled").checked = true;
                } else if(value == 'false') {
                    document.getElementById("unlabeled").checked = true;
                }
            } else if(name == 'reviewed') {
                if(value == 'true') {
                    document.getElementById("reviewed").checked = true;
                } else if(value == 'false') {
                    document.getElementById("unreviewed").checked = true;
                }
            }
        }
    }

}

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

function checkExtension(filePath) {
    var valid_extensions = [".mp3", ".wav", ".mp4"];

    var file = filePath.value;
    var files_extension = file.substr(file.length - 4, 4);
    
    if(!valid_extensions.includes(files_extension)) {
        document.getElementById("import-file").value = "";
        alert("The format " + files_extension + " is not accepted. Please upload another file.");
    }
}
// $("#import-file").change(function(){
    
// });

window.onload = fixFilters;

