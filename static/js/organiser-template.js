let currentTab = 0;
showTab(currentTab);

getRegisteredTemplate(0);

var gheetslist = [];

var spreadsheet_url = '';
var sheetname = '';
var templateColumns = [];
var jsonGsheetData = [];
var gsheetColumns = [];
var ColumnMappingJson = [];
var sampleDataJson = [];
var gsheet_columnwise_data = []

var final_response = []; //PDFfolder_url, pdf_urls

function showTab(n) {
    let x = document.getElementsByClassName("step");
    try{
        x[n].style.display = "block";
        let progress = (n / (x.length - 1)) * 100;
        document.querySelector(".progress-bar").style.width = progress + "%";
        document.querySelector(".progress-bar").setAttribute("aria-valuenow", progress);
        document.getElementById("prevBtn").style.display = n == 0 ? "none" : "inline";
        document.getElementById("nextBtn").innerHTML = n == x.length - 1 ? "Submit" : "Next";
    }
    catch(e){
    console.log(e);
    }
}

function nextPrev(n) {
    let x = document.getElementsByClassName("step");
    console.log('x.length: ', x.length);
    console.log('currentTab: ', currentTab);
//    if (n == 1 && !validateForm()) return false;
    if (currentTab < x.length-1) {
        x[currentTab].style.display = "none";
    }
    currentTab += n;

    if (currentTab >= x.length) {
        generateCertGdrive(0);
//        document.getElementById('final-step').style.display = 'block';
//        resetForm();
        return false;
    }
    showTab(currentTab);
}

function validateForm() {
    let valid = true;
    let x = document.getElementsByClassName("step");
    let y = x[currentTab].getElementsByTagName("input");
    for (var i = 0; i < y.length; i++) {
        if (y[i].value == "") {
            y[i].className += " invalid";
            valid = false;
        }
    }
    return valid;
}

function resetForm() {
    let x = document.getElementsByClassName("step");
    for (var i = 0; i < x.length; i++) {
        x[i].style.display = "none";
    }
    let inputs = document.querySelectorAll("input");
    inputs.forEach(input => {
        input.value = "";
        input.className = "";
    });
    currentTab = 0;
    showTab(currentTab);
    document.querySelector(".progress-bar")
        .style.width = "0%";
    document.querySelector(".progress-bar")
        .setAttribute("aria-valuenow", 0);
    document.getElementById("prevBtn")
        .style.display = "none";
}

//verify the google sheet
//var verifyGsheetBtn = document.getElementById('verify-gsheet');
//verifyGsheetBtn.addEventListener('click', fetchData);

function verifyGsheet() {
            document.getElementById("loader1").style.display = 'block';
//            document.getElementById("myProgress").style.display = 'block';
//            move();

            // You can add your logic here to perform a POST request with the selected data
            // For now, I'm just logging the selected data to the console
            spreadsheet_url = document.getElementById("spreadsheet_url").value;
            sheetname = document.getElementById("sheetname").value;
            var password = document.getElementById("password").value;

            console.log("Selected spreadsheet_url:", spreadsheet_url);
            console.log("Selected sheetname:", sheetname);
            console.log("Selected password:", password);

            // If you want to perform a POST request, you can use the fetch API here
            // Example:
            fetch("/fetchgsheet", {
                 method: "POST",
                 headers: {
                     "Content-Type": "application/json",
                 },
                 body: JSON.stringify({
                     spreadsheet_url: spreadsheet_url,
                     sheetname: sheetname,
                     password: password,
                 }),
             })
             .then(response => response.json())
             .then(data => {
                    document.getElementById("loader1").style.display = 'block';
//                    document.getElementById("myProgress").style.display = 'block';
//                    move();
                    console.log("Submit response:", data);
                    populateTable(data);

                    if (data==[] || data=='' || data==null){
                        document.getElementById('sample-gsheet-result').style.display = 'none';
                    }
                    else{
                    document.getElementById('sample-gsheet-result').style.display = 'block';

                    }
                    })
             .catch(error => console.error('Error submitting data:', error));


}


function populateTable(data) {
//    move();
    var table = document.getElementById('verifyGsheetTable');

    // Clear existing rows
    table.innerHTML = '';

    // Create header row
    var headerRow = table.insertRow(0);
    console.log('headerRow: ', headerRow);
    for (var key in data[0]) {
        var th = document.createElement('th');
        th.textContent = key;
        headerRow.appendChild(th);
    }


    var rowCount = Math.min(2, data.length); // Limit to first 5 entries or data length if less than 5
    for (var i = 0; i < rowCount; i++) {
        var rowData = data[i];
        var row = table.insertRow(i + 1);
        for (var key in rowData) {
            var cell = row.insertCell();
            cell.textContent = rowData[key];
        }
    }


    // Create data rows
//    data.forEach(function (rowData, index) {
//        var row = table.insertRow(index + 1);
//        for (var key in rowData) {
//            var cell = row.insertCell();
//            cell.textContent = rowData[key];
//        }
//    });

    document.getElementById("loader1").style.display = 'none';
//    document.getElementById("myProgress").style.display = 'none';

    var table = document.getElementById("verifyGsheetTable");
    jsonGsheetData = data;//tableToJson(table);
    console.log(jsonGsheetData);
    gsheetColumns = Object.keys(jsonGsheetData[0]);
    addRowsBasedOnTemplateColumns();
//    extractColumnDataToJson();
    populateSampleInputTable();
}

// improvement: use cache storage, add refresh button to load and download from web


function getRegisteredTemplate(refresh){
    if (document.getElementById("loader1")!= null){
        document.getElementById("loader1").style.display = 'block';
    }
    console.log('triggered!!');
    console.log("/getRegisteredTemplate/?refresh="+refresh);
    fetch("/getRegisteredTemplate/?refresh="+refresh, {
        method: "get",
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
//        const registeredTemplateData = data;
        document.getElementById("allTemplateData").value = data;

        document.getElementById("loader1").style.display = 'none';
        document.getElementById("Searching-Template").style.display = 'none';
        const selectElement = document.getElementById("Template-List");

        // Clear existing options
        selectElement.innerHTML = "";

        // Create default option
            const defaultOption = document.createElement("option");
            defaultOption.value = ""; // Set value as needed
            defaultOption.textContent = "Select Template"; // Display text for the default option
            selectElement.appendChild(defaultOption);

        // Iterate through JSON data and create options
        data.forEach(template => {
            const option = document.createElement("option");
            option.value = template.id;  // Assign value based on your requirement
            option.textContent = template.name;  // Display text for the option
            selectElement.appendChild(option);
        });
    })
}

function selectRegisteredTemplate(){
    var optionValue = document.getElementById("Template-List").value;
    console.log(optionValue);
    const t_data = document.getElementById("allTemplateData").value;

    t_data.forEach(t => {
//        console.log(optionValue);
//        console.log(t['name']);
        if (t['id'] == optionValue){
            document.getElementById('docx-cols').innerHTML = '';
            document.getElementById('docx-cols').style.display = 'block';
            templateColumns = t['variable'];
            console.log(t['variable']);
            getTemplateColumns(t['variable']);
        }
    })

//    document.getElementById("output").innerHTML = optionValue;
}

function getTemplateColumns(columns){
    document.getElementById("docx-cols-div").style.display = 'block';
    document.getElementById("docx-cols").style.display = 'block';
    const colElement = document.getElementById("docx-cols");
    columns.forEach(template => {
        const span = document.createElement("span");
        span.className = 'badge bg-dark';
        span.style = 'margin-right:5px';
        span.innerHTML = template;
        colElement.appendChild(span);

        document.getElementById('embedded-template-cert-dev').style.display = 'block';
        document.getElementById('embedded-template-cert').style.display = 'block';
        document.getElementById("embedded-template-cert").src = 'https://drive.google.com/file/d/'+document.getElementById("Template-List").value+'/preview';
//        embeddedTemplate();
    })
}





function tableToJson(table) {
    var data = [];

    // Iterate through rows (skip the first row which usually contains headers)
    for (var i = 1; i < table.rows.length; i++) {
        var tableRow = table.rows[i];
        var rowData = {};

        // Iterate through cells of current row
        for (var j = 0; j < tableRow.cells.length; j++) {
            var cell = tableRow.cells[j];
            var cellKey = table.rows[0].cells[j].innerHTML.trim(); // Use header as key
            var cellValue = cell.innerHTML.trim(); // Use cell content as value

            // Add key-value pair to row data object
            rowData[cellKey] = cellValue;
        }

        // Add row data object to data array
        data.push(rowData);
    }

    return data;
}

function map_cols(){

}

//
//async function sleep(ms) {
//    return new Promise(resolve => setTimeout(resolve, ms));
//}
//
//var loader_i = 0;
//async function move() {
//  if (loader_i == 0) {
//    loader_i = 1;
//    var elem = document.getElementById("myBar");
//    var width = 1;
//    var id = setInterval(frame, 8);
//    function frame() {
//      if (width >= 100) {
//        clearInterval(id);
//        loader_i = 0;
//      } else {
//        width++;
//        elem.style.width = width + "%";
//      }
//    }
//
//  }
//  if (loader_i == 1) {
//    await sleep(1000);
//    move();
//    loader_i = 0;
//
//  }
//}

//this part is for mapping metadata
function addRowsBasedOnTemplateColumns() {
    document.getElementById("columnmapping-tbody").innerHTML = '';
    var table = document.getElementById("mappingTable");

    var tr_rows = table.getElementsByTagName("tr");
    for (var i = tr_rows.length - 1; i > 0; i--) {
         table.deleteRow(i);
    }
    // Iterate over templateColumns
    templateColumns.forEach(templateCol => {
        // Skip processing for "RNUM"
        if (templateCol === "RNUM") {
            return;
        }

        var row = table.insertRow();

        // Cells for templateColumns
        var cellTemplate = row.insertCell();
        cellTemplate.textContent = templateCol;

        // Cells for gsheetColumns dropdown
        var cellGsheet = row.insertCell();
        var selectGsheet = document.createElement("select");
        selectGsheet.classList.add("form-select");
        selectGsheet.classList.add("gsheet-column");
        gsheetColumns.forEach(column => {
            var option = document.createElement("option");
            option.text = column;
            selectGsheet.add(option);
            if (column === templateCol) {
                option.selected = true;
            }
        });
        var otherOption = document.createElement("option");
        otherOption.text = "others";
        selectGsheet.add(otherOption);
        cellGsheet.appendChild(selectGsheet);

        // Cells for hardcode_value_ifapplicable input
        var cellHardcode = row.insertCell();
        var inputHardcode = document.createElement("input");
        inputHardcode.type = "text";
        inputHardcode.classList.add("hardcode-value");
        inputHardcode.style.display = "none"; // Initially hidden
        cellHardcode.appendChild(inputHardcode);

        // Event listener to show/hide input based on gsheetColumns selection
        selectGsheet.addEventListener("change", function() {
            var selectedValue = selectGsheet.value;
            inputHardcode.style.display = selectedValue === "others" ? "block" : "none";
        });

        // Set initial display state based on initial value
        if (selectGsheet.value === "others") {
            inputHardcode.style.display = "block";
        } else {
            inputHardcode.style.display = "none";
        }
    });
    extractColumnDataToJson();
}



function extractColumnDataToJson() {
    var table = document.getElementById("mappingTable");
    var jsonData = [];
    // Iterate through rows (skip the header row)
    for (var i = 1; i < table.rows.length; i++) {
        var row = table.rows[i];
        var templateCol = row.cells[0].textContent.trim();
        var gsheetCol = row.cells[1].querySelector(".gsheet-column").value;
        var hardcodeValue = row.cells[2].querySelector(".hardcode-value").value;

        // Construct an object and add to jsonData array
        var rowData = {
            templateColumns: templateCol,
            gsheetColumns: gsheetCol,
            hardcode_value_ifapplicable: hardcodeValue
        };
        jsonData.push(rowData);
    }
    ColumnMappingJson = jsonData;

    // Return JSON data as string
    return jsonData; //JSON.stringify(jsonData, null, 2);
}


//sampleData table
function populateSampleInputTable() {
        extractColumnDataToJson();
        document.getElementById("tableBody").innerHTML = '';
        var table = document.getElementById("sampleInputTable").getElementsByTagName("tbody")[0];

        ColumnMappingJson.forEach(item => {
            var row = table.insertRow();

            // Cell for templateColumns
            var cellTemplateColumns = row.insertCell();
            cellTemplateColumns.textContent = item.templateColumns;

            // Cell for Sample Value (text input or hardcode_value_ifapplicable)
            var cellSampleValue = row.insertCell();
            if (item.gsheetColumns === "others") {
                // Show hardcode_value_ifapplicable for "Others"
                cellSampleValue.textContent = item.hardcode_value_ifapplicable;
            } else {
                // Show text input for other gsheetColumns
                var input = document.createElement("input");
                input.type = "text";
                input.value = ""; // You can set initial value here if needed
                cellSampleValue.appendChild(input);
            }
        });
        collectSampleData();
    }


//sample data collection to show in iframe
function collectSampleData() {
        var table = document.getElementById("sampleInputTable").getElementsByTagName("tbody")[0];
        var rowData = [];

        // Iterate through table rows
        for (var i = 0; i < table.rows.length; i++) {
            var row = table.rows[i];
            var templateColumns = row.cells[0].textContent.trim();
            var sampleValue;

            if (row.cells[1].querySelector("input")) {
                // If there's an input field, get its value
                sampleValue = row.cells[1].querySelector("input").value;
            } else {
                // Otherwise, get the text content
                sampleValue = row.cells[1].textContent.trim();
            }

            // Construct object and add to array
            var rowDataItem = {
                templateColumns: templateColumns,
                sampleValue: sampleValue
            };
            rowData.push(rowDataItem);
        }

        // Log the collected data to console
        console.log("Collected Data:", rowData);
        sampleDataJson = rowData;

        // Optionally, you can use the collected data as needed in your application
        // For example, send it to a server, process it further, etc.
    }


//generate sample certificate from the sample data
function generateSampleCert(){
    document.getElementById("loader1").style.display = 'block';
    fetch("/generateSampleCert", {
                 method: "POST",
                 headers: {
                     "Content-Type": "application/json",
                 },
                 body: JSON.stringify({
                     template_id: document.getElementById("Template-List").value,
                     sample_data: sampleDataJson
                 }),
             })
             .then(response => response.json())
             .then(data => {
                    console.log(data);
                    document.getElementById('embedded-sample-cert').style.display = 'block';
                    document.getElementById('embedded-sample-cert').src = data;
                    document.getElementById("loader1").style.display = 'none';
             })

}

function generateCertGdrive(is_sample){
    document.getElementById("loader1").style.display = 'block';
    if (is_sample==1){
    gsheet_columnwise_data = [];
    let gsheet_columnwise_element = {};

    sampleDataJson.forEach(item => {
        gsheet_columnwise_element[item.templateColumns] = item.sampleValue;
    });
    gsheet_columnwise_data.push(gsheet_columnwise_element);
    }
    else{
        gsheet_columnwise_data = jsonGsheetData;
    }
    console.log(gsheet_columnwise_data);

    fetch("/generateCertGdrive", {
             method: "POST",
             headers: {
                "Content-Type": "application/json",
             },
             body: JSON.stringify({
                is_sample: is_sample,
                template_id: document.getElementById("Template-List").value,
                spreadsheet_url: spreadsheet_url,
                sheetname: sheetname,
                gsheet_columnwise_data: gsheet_columnwise_data,
                column_mapping: ColumnMappingJson,
             }),
         })
         .then(response => response.json())
         .then(data => {
            console.log(data);
            final_response = data;

            if (final_response.pdf_urls && is_sample == 1){
                document.getElementById('embedded-sample-cert').style.display = 'block';
                document.getElementById('embedded-sample-cert').src = final_response.pdf_urls[0];
                document.getElementById("loader1").style.display = 'none';
            }
//            else{
//                openModal();
//                document.getElementById('embedded-sample-cert').style.display = 'none';
//            }

            if (is_sample == 0){
                openModal();
            }



            return data['PDFfolder_url'];
         })
}










function loadGoogleSheetsDropdowns() {
    fetch('/get_gsheetslist')
        .then(response => response.json())
        .then(data => {
            gheetslist = data;
            populateGsheetDropdown(data);
        })
        .catch(error => {
            console.error('Error fetching Google Sheets list:', error);
        });
}

function populateGsheetDropdown(sheetData) {
    var selectGsheet = document.getElementById("selectGsheet");

    // Clear existing options
    selectGsheet.innerHTML = "";

    if (sheetData.length === 0) {
        selectGsheet.innerHTML = '<option value="">No Google Sheets found</option>';
    } else {
        // Create default option
        var defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "Select a Google Sheets file...";
        selectGsheet.appendChild(defaultOption);

        // Populate dropdown with sheetData
        sheetData.forEach(function(item) {
            var option = document.createElement("option");
            option.value = item.gsheet_url;
            option.textContent = item.fileName;
            selectGsheet.appendChild(option);
        });

        // Event listener for when Google Sheets file is selected
        selectGsheet.addEventListener('change', function() {
            console.log()
            fetchSheetNames(selectGsheet.value);
        });
    }
}

function fetchSheetNames(selectedGsheetUrl) {
    if (!selectedGsheetUrl) {
        clearSheetDropdown();
        return;
    }
    for (var i=0; gheetslist.length; i++){
        if (gheetslist[i]['gsheet_url'] == selectedGsheetUrl){
            populateSheetDropdown(gheetslist[i]['sheets']);
            break;
        }
    }
}
//
//function fetchSheetNames(selectedGsheetUrl) {
//    if (!selectedGsheetUrl) {
//        clearSheetDropdown();
//        return;
//    }
//
//    fetch(selectedGsheetUrl)
//    .then(response => {
//        if (!response.ok) {
//            throw new Error('Network response was not ok');
//        }
//        return response.text(); // Get the raw text response
//    })
//    .then(text => {
//        console.log("Raw response text:", text); // Log the raw response text
//        try {
//            var data = JSON.parse(text); // Attempt to parse the JSON
//            console.log("Parsed JSON data:", data);
//            populateSheetDropdown(data[0].sheets); // Assuming you want sheets from the first file only
//        } catch (error) {
//            console.error('Error parsing JSON:', error);
//            clearSheetDropdown();
//        }
//    })
//    .catch(error => {
//        console.error('Error fetching or parsing sheet names:', error);
//        clearSheetDropdown();
//    });
//}

function populateSheetDropdown(sheetNames) {
    var selectSheet = document.getElementById("selectSheet");

    // Clear existing options
    selectSheet.innerHTML = "";

    // Create default option
    var defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Select a sheet...";
    selectSheet.appendChild(defaultOption);

    // Populate dropdown with sheet names
    sheetNames.forEach(function(sheet) {
        var option = document.createElement("option");
        option.value = sheet.name;
        option.textContent = sheet.name;
        selectSheet.appendChild(option);
    });
}

function clearSheetDropdown() {
    var selectSheet = document.getElementById("selectSheet");
    selectSheet.innerHTML = '<option value="">Select a sheet...</option>';
}

// Call the function to start loading the dropdowns
loadGoogleSheetsDropdowns();



function verifyGsheet_automatic() {
            document.getElementById("loader1").style.display = 'block';
//            document.getElementById("myProgress").style.display = 'block';
//            move();

            // You can add your logic here to perform a POST request with the selected data
            // For now, I'm just logging the selected data to the console
             spreadsheet_url = document.getElementById('selectGsheet').value;
             sheetname = document.getElementById('selectSheet').value;
            var password = '123'//document.getElementById("password").value;

            console.log("Selected spreadsheet_url:", spreadsheet_url);
            console.log("Selected sheetname:", sheetname);
            console.log("Selected password:", password);

            // If you want to perform a POST request, you can use the fetch API here
            // Example:
            fetch("/fetchgsheet", {
                 method: "POST",
                 headers: {
                     "Content-Type": "application/json",
                 },
                 body: JSON.stringify({
                     spreadsheet_url: spreadsheet_url,
                     sheetname: sheetname,
                     password: password,
                 }),
             })
             .then(response => response.json())
             .then(data => {
                    document.getElementById("loader1").style.display = 'block';
//                    document.getElementById("myProgress").style.display = 'block';
//                    move();
                    console.log("Submit response:", data);
                    populateTable(data);

                    if (data==[] || data=='' || data==null){
                        document.getElementById('sample-gsheet-result').style.display = 'none';
                    }
                    else{
                    document.getElementById('sample-gsheet-result').style.display = 'block';

                    }
                    })
             .catch(error => {
             document.getElementById('sample-gsheet-result').style.display = 'none';
             console.error('Error submitting data:', error);
             })
}

function embeddedTemplate(){
    document.getElementById("loader1").style.display = 'block';
    fetch("/embeddedTemplate", {
        method:"POST",
        body: JSON.stringify({
                  template_id: document.getElementById("Template-List").value
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        document.getElementById('embedded-template-cert').style.display = 'block';
        document.getElementById('embedded-template-cert').src = data;
        document.getElementById("loader1").style.display = 'none';
    })
}


// Function to open the modal
 function openModal() {
    document.getElementById("loader1").style.display = 'block';
    var myModal = new bootstrap.Modal(document.getElementById('staticBackdrop'), {
      backdrop: 'static', // Optional: 'static' for a modal that doesn't close when clicking outside
      keyboard: false     // Optional: false to disable closing the modal with the Escape key
    });

    console.log("final_response['PDFfolder_url']: ", final_response['PDFfolder_url']);

    fetch("/downloadPdfZip", {
        method:"POST",
        body:JSON.stringify({
            folder_url: final_response['PDFfolder_url'],
        })

    })
    .then(response => response.json())
    .then(data => {
        console.log('downloadPdfZip: ', data);
        document.getElementById('download_zip_a').href = data['url'];
        document.getElementById("loader1").style.display = 'none';
        myModal.show();
    })

 }

 // Function to close the modal
 function closeModal() {
    var modalElement = document.getElementById('staticBackdrop');
    var modal = bootstrap.Modal.getInstance(modalElement);
    modal.hide();
 }