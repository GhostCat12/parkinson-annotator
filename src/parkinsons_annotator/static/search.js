const form = document.getElementById("search-form");
const searchBox = document.getElementById("search-box");
const searchCategory = document.getElementById("search-category");
const searchClassification = document.getElementById("search-classification-dropdown")
const uploadForm = document.getElementById("upload-form");
const loadingIndicator = document.getElementById("loading");
const uploadButton = document.getElementById("upload-btn");
const resultsPanel = document.getElementById("results-panel");

// Load Google Charts
google.charts.load('current', {'packages':['corechart']});

// Graceful shutdown
window.addEventListener("beforeunload", function () {
    navigator.sendBeacon("/shutdown");
});

const render_pie_chart = (data, chartField = 'classification') => {
    const results = data.results;

    // Count occurrences of each value in the specified field
    const counts = {};
    results.forEach(row => {
        const value = row[chartField] || 'Unknown';
        counts[value] = (counts[value] || 0) + 1;
    });

    // Determine chart title based on field
    const chartTitle = chartField === 'gene_symbol'
        ? 'Gene Distribution'
        : 'ClinVar Classification Distribution';

    var chartData = google.visualization.arrayToDataTable([
        [chartField === 'gene_symbol' ? 'Gene' : 'Classification', 'Count'],
        ...Object.entries(counts).map(([key, value]) => [key, value])
    ]);

    var options = {
        title: chartTitle,
        titleTextStyle: { fontSize: 18, color: '#546e7a' },
        colors: ['#c51c22', '#1cc5bf', '#c51c76', '#c56b1c', '#e56e6f', '#008a7e', '#ef67ac', '#dc9f3a'],
        fontSize: 14,
        pieHole: 0.4,
        legend: { position: 'labeled', textStyle: { fontSize: 13 } },
        chartArea: { left: '15%', top: '15%', width: '70%', height: '70%' },
        pieSliceText: 'none'
    };

    var chart = new google.visualization.PieChart(document.getElementById('piechart'));

    chart.draw(chartData, options);
}

// Handle upload
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', document.getElementById('upload-file-input').files[0]);

    loadingIndicator.style.display = 'block';
    uploadButton.disabled = true;

    const res = await fetch('/upload', { method: 'POST', body: formData });

    loadingIndicator.style.display = 'none';
    uploadButton.disabled = false;

    // alert(res.ok ? 'File uploaded successfully!' : 'Upload failed.');

    const message = await res.text();   // <-- read the server message
    alert(message);                     // <-- show it directly
});

// Handle search

// Toggle search input depending on category
searchCategory.addEventListener("change", function () {
    if (searchCategory.value === "classification") {
        searchBox.style.display = "none";
        searchBox.required = false;

        searchClassification.style.display = "inline-block";
        searchClassification.required = true;
    } else {
        searchBox.style.display = "inline-block";
        searchBox.required = true;

        searchClassification.style.display = "none";
        searchClassification.required = false;
    }
});

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const selectedCategory = searchCategory.value;
    const query = searchBox.value.trim();
    const selectedSearchClassification = searchClassification.value;

    resultsPanel.style.display = 'block';

    // Always get the containers fresh
    const resultsList = document.getElementById("results");

    // Clear old outputs
    resultsList.innerHTML = "";
    document.getElementById("piechart").innerHTML = "";

    const response = await fetch("/search", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            query,
            searchClassification: selectedSearchClassification,
            searchCategory: selectedCategory
        }),
    });

    const data = await response.json();

    console.log("JSON received:", data);

    let resultSentence = "";

    if (selectedCategory === "variant") {
        resultSentence = `Variant: <strong>${query}</strong>`;

    } else if (selectedCategory === "gene_symbol") {
        resultSentence = `Patient variants found in gene <strong>${query}</strong>:`;

    } else if (selectedCategory === "classification") {
        if (selectedSearchClassification === "Not found in Clinvar") {
            resultSentence = 'Patient variants which were not identified in ClinVar:';
        } else {
            resultSentence = `Patient variants with ClinVar classification: <strong>${selectedSearchClassification}</strong>:`;
        }
    } else if (selectedCategory === "patient_name") {
        if (query === "patient") {
            resultSentence = 'Variants found in all patients:';
        } else
            resultSentence = `Variants identified in  <strong>${query}</strong>:`;
    } else {
        resultSentence = `${selectedCategory} found in <strong>${query}</strong>`;
    }

    resultsList.innerHTML = `<p class="result-header">${resultSentence}</p>`;

    // Handle errors
    if (data.message) {
        resultsList.innerHTML = data.message;
        return;
    }

    // SPECIAL CASE: VARIANT SEARCH
    if (selectedCategory === "variant") {
        const variantData = data.results.variant;
        const patients = data.results.patients;
        const piechart = document.getElementById("piechart");

        // Left column: Patients header + chips
        const patientsHeader = document.createElement("h3");
        patientsHeader.classList.add("variant-section-header");
        patientsHeader.textContent = "Patients";
        resultsList.appendChild(patientsHeader);

        const container = document.createElement("div");
        container.classList.add("patient-chips-container");

        patients.forEach(p => {
            const chip = document.createElement("span");
            chip.classList.add("patient-chip");
            chip.textContent = p;
            container.appendChild(chip);
        });

        resultsList.appendChild(container);

        // Right column: Variant info table (use piechart area)
        const variantHeader = document.createElement("h3");
        variantHeader.classList.add("variant-section-header");
        variantHeader.textContent = "Variant Information";
        piechart.appendChild(variantHeader);

        const table = document.createElement("table");
        table.classList.add("variant-info-table");

        for (const [key, value] of Object.entries(variantData)) {
            const row = document.createElement("tr");

            const th = document.createElement("th");
            th.classList.add("variant-info-header-cell");
            th.textContent = key;

            const td = document.createElement("td");
            td.classList.add("variant-info-data-cell");
            td.innerHTML = value;    // allows clickable links

            row.appendChild(th);
            row.appendChild(td);
            table.appendChild(row);
        }

        piechart.appendChild(table);

        return;  // stop - don't trigger normal results handler
    }

    // Chart by gene for classification searches, otherwise by classification
    const chartField = selectedCategory === 'classification' ? 'gene_symbol' : 'classification';
    render_pie_chart(data, chartField);

    const results = data.results;

    if (!results || results.length === 0) {
        resultsList.innerHTML = "No matches found";
        return;
    }

    // Determine table columns based on what Flask returned
    const columns = data.column_order || Object.keys(results[0]);

    // Build a table dynamically

    const table = document.createElement("table");
    table.classList.add("results-table");

    const headerRow = document.createElement("tr");
    headerRow.classList.add("table-row");

    columns.forEach(col => {
        const th = document.createElement("th");
        th.classList.add("table-header");
        th.textContent = col.replace("_", " ").toUpperCase();
        headerRow.appendChild(th);
    });

    table.appendChild(headerRow);

    // Fill table rows
    results.forEach(row => {
        const tr = document.createElement("tr");
        tr.classList.add("table-row");

        columns.forEach(col => {
            const td = document.createElement("td");
            td.classList.add("table-cell");
            const value = row[col];

            if (typeof value === "string") {
                const cleaned = value.replace(/[\[\]']/g, "").trim();

                if (cleaned.includes("http")) {
                    td.innerHTML = `<a href="${cleaned}" target="_blank">${cleaned}</a>`;
                } else {
                    td.textContent = cleaned;
                }
            } else {
                td.textContent = value;
            }

            tr.appendChild(td);
        });

        table.appendChild(tr);
    });

    resultsList.appendChild(table);

});