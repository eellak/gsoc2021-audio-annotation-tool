var selected_export_format = null;

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

// filter tasks on project page
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

// when a file is uploaded
function checkExtension(filePath) {
    var valid_extensions = [".mp3", ".wav", ".mp4", ".zip"];

    var file = filePath.value;
    var files_extension = file.substr(file.length - 4, 4);
    
    if(!valid_extensions.includes(files_extension)) {
        document.getElementById("import-file").value = "";
        alert("The format " + files_extension + " is not accepted. Please upload another file.");
    }
}

// dix for export click
function selectExportFormat(div) {

    // execute only if div not already selected
    if(selected_export_format != div) {
        let export_div_json = document.getElementById('export_div_json');
        let json_radio = document.getElementById('json_radio');
        let export_div_csv = document.getElementById('export_div_csv');
        let csv_radio = document.getElementById('csv_radio');

        if(export_div_json == div) {

            // select json div
            selected_export_format = export_div_json;
            export_div_json.style.backgroundColor = 'rgba(115, 223, 237, 0.3)';
            export_div_json.style.cursor = 'default';
            json_radio.checked = true;

            // unselect csv div
            export_div_csv.style.backgroundColor = 'white';
            export_div_csv.style.cursor = 'pointer';
            csv_radio.checked = false;
        } else {

            // select csv div
            selected_export_format = export_div_csv;
            export_div_csv.style.backgroundColor = 'rgba(115, 223, 237, 0.3)';
            export_div_csv.style.cursor = 'default';
            csv_radio.checked = true;

            // unselect json div
            export_div_json.style.backgroundColor = 'white';
            export_div_json.style.cursor = 'pointer';
            json_radio.checked = false;
        }
    }
}

// export annotations for project request
function exportDataRequest() {
}

document.addEventListener('DOMContentLoaded', function() {
    fixFilters();
    selected_export_format = document.getElementById('export_div_json');
});