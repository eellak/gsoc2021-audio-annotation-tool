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
// function checkExtension(filePath) {
//     var valid_extensions = [".mp3", ".wav", ".mp4", ".zip"];

//     var file = filePath.value;
//     var files_extension = file.substr(file.length - 4, 4);
    
//     if(!valid_extensions.includes(files_extension)) {
//         document.getElementById("import-file").value = "";
//         alert("The format " + files_extension + " is not accepted. Please upload another file.");
//     }
// }

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

// download exported file
function downloadExportedFile(result, status) {

    let format = result['format'];
    let exported_json = result['exported_json'];
    let exported_name = result['exported_name'];
    if(format == "JSON") {
        downloadJSON(JSON.stringify(exported_json), exported_name, 'text/plain');
        showAlert(result['message'], status);
    } else if(format == "CSV") {
        downloadCSV(exported_json, exported_name);
        showAlert(result['message'], status);
    } else {
        // something is wrong
    }
}

function showAlert(message, status) {
    $('#exportModal').modal('toggle');
    if(status == 200) {
        // success message
        document.getElementById('export_success_alert').style.display = 'block';
        $("#success_message").html(message);
        $('#export_success_alert').addClass('show');
    } else if(status == 400 || status == 401) {
        // danger message
        document.getElementById('export_fail_alert').style.display = 'block';
        $("#fail_message").html(message);
        $('#export_fail_alert').addClass('show');
    }
}

function hideAlert(button) {
    if(button.value == "SUCCESS") {
        document.getElementById('export_success_alert').style.display = 'none';
        $('#export_success_alert').removeClass('show');
    } else if(button.value == "DANGER") {
        document.getElementById('export_fail_alert').style.display = 'none';
        $('#export_fail_alert').removeClass('show');
    }
}

function downloadJSON(content, fileName, contentType) {
    let a = document.createElement("a");
    let file = new Blob([content], { type: contentType });
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
}

function downloadCSV(content, fileName) {
    let rows = [
        ["audio", "audio_length", "id", "regions", "completed_at", "annotator_email", "annotator_username", "annotation_id", "project_id"]
    ];
    
    for(task of content) {
        for(annotation of task['annotations']) {
            let regions = []
            for(region of annotation['result']) regions.push(region['value'])

            var arr = [
                task['data']['audio'],
                annotation['result'][0]['audio_length'],
                task['id'],
                '"' + JSON.stringify(regions) + '"',
                JSON.stringify(annotation['created_at']),
                annotation['completed_by']['email'],
                annotation['completed_by']['username'],
                annotation['id'],
                task['project']
            ];
        }
        rows.push(arr);
    }

    let csvContent = "data:text/csv;charset=utf-8," + rows.map(e => e.join(",")).join("\n");
    // console.log(csvContent);
    let encodedUri = encodeURI(csvContent);
    let a = document.createElement("a");
    a.href = encodedUri;
    a.download = fileName;
    a.click();
}

// export annotations for project request
function exportDataRequest() {
    // xmlhttp request for exporting data
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // Typical action to be performed when the document is ready:
           downloadExportedFile(JSON.parse(this.responseText), this.status);
        } else if(this.readyState == 4 && (this.status == 400 || this.status == 401)) {
            showAlert(JSON.parse(this.responseText)['message'], this.status);
        }
    };
    let url = host + "api/v1/projects/" + project_id + "/tasks/export";
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader("X-CSRFToken", django_csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify($("input[name=exampleRadios]:checked").val()));
}

document.addEventListener('DOMContentLoaded', function() {
    fixFilters();
    selected_export_format = document.getElementById('export_div_json');

    // progress bar
    const import_form = document.getElementById('import-form');
    console.log(import_form);
});