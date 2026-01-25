// Graceful shutdown
window.addEventListener("beforeunload", function () {
    navigator.sendBeacon("/shutdown");
});

// Handle upload
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', document.getElementById('upload-file-input').files[0]);

    document.getElementById('loading').style.display = 'block';
    document.getElementById('upload-btn').disabled = true;

    const res = await fetch('/upload', { method: 'POST', body: formData });

    document.getElementById('loading').style.display = 'none';
    document.getElementById('upload-btn').disabled = false;

    // alert(res.ok ? 'File uploaded successfully!' : 'Upload failed.');

    const message = await res.text();   // <-- read the server message
    alert(message);                     // <-- show it directly
});

// Handle search

const form = document.getElementById("search-form");
const searchBox = document.getElementById("search-box");
const searchCategory = document.getElementById("search-category");
const searchClassification = document.getElementById("search-classification-dropdown")

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

    // Always get the containers fresh
    const resultsList = document.getElementById("results");
    const variantDict = document.getElementById("variant-dict");
    const patientList = document.getElementById("patient-list");

    // Clear old outputs
    resultsList.innerHTML = "";
    variantDict.innerHTML = "";
    patientList.innerHTML = "";

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
        resultSentence = `Patients with variant <strong>${query}</strong>:`;

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
        const variantData = data.variant;
        const patients = data.patients;

        // Patient list
        const ul = document.createElement("ul");
        ul.style.listStyleType = "none";
        ul.style.padding = "0";
        ul.style.margin = "0 auto";

        const container = document.createElement("div");
        container.style.textAlign = "center";
        container.style.marginTop = "20px";
        container.style.fontFamily = "Georgia, serif";
        container.style.fontSize = "22px";     // bigger text
        container.style.fontWeight = "bold";

        patients.forEach(p => {
            const li = document.createElement("li");
            li.textContent = p;
            li.style.margin = "5px 0";
            ul.appendChild(li);
        });

        container.appendChild(ul);
        patientList.appendChild(container);

        // ADD HEADER BETWEEN PATIENT LIST AND TABLE
        const header = document.createElement("h3");
        header.textContent = "Variant Information";
        header.style.textAlign = "center";
        header.style.fontFamily = "Georgia, serif";
        header.style.fontSize = "26px";
        header.style.marginTop = "25px";
        header.style.marginBottom = "10px";

        variantDict.appendChild(header);

        // Build variant info table
        const table = document.createElement("table");
        table.style.margin = "20px auto";
        table.style.borderCollapse = "collapse";

        for (const [key, value] of Object.entries(variantData)) {
            const row = document.createElement("tr");

            const th = document.createElement("th");
            th.textContent = key;
            th.style.border = "1px solid black";
            th.style.padding = "6px 10px";

            const td = document.createElement("td");
            td.innerHTML = value;    // allows clickable links
            td.style.border = "1px solid black";
            td.style.padding = "6px 10px";

            row.appendChild(th);
            row.appendChild(td);
            table.appendChild(row);
        }

        variantDict.appendChild(table);

        return;  // stop - don't trigger normal results handler
    }

    const results = data.results;

    if (!results || results.length === 0) {
        resultsList.innerHTML = "No matches found";
        return;
    }

    // Determine table columns based on what Flask returned
    const columns = data.column_order || Object.keys(results[0]);

    // Build a table dynamically

    const table = document.createElement("table");
    table.style.margin = "20px auto";
    table.style.borderCollapse = "collapse";
    table.style.fontFamily = "Georgia, serif";
    table.style.fontSize = "18px";

    const header = document.createElement("tr");

    columns.forEach(col => {
        const th = document.createElement("th");
        th.textContent = col.replace("_", " ").toUpperCase();
        th.style.padding = "10px 15px";
        th.style.backgroundColor = "#e0e0e0";
        th.style.border = "1px solid black";
        header.appendChild(th);
    });

    table.appendChild(header);

    // Fill table rows
    results.forEach(row => {
        const tr = document.createElement("tr");

        columns.forEach(col => {
            const td = document.createElement("td");
            const value = row[col];

            if (typeof value === "string") {
                let cleaned = value.replace(/[\[\]']/g, "").trim();

                if (cleaned.includes("http")) {
                    td.innerHTML = `<a href="${cleaned}" target="_blank">${cleaned}</a>`;
                } else {
                    td.textContent = cleaned;
                }
            } else {
                td.textContent = value;
            }

            td.style.padding = "8px 12px";
            td.style.border = "1px solid black";
            tr.appendChild(td);
        });

        table.appendChild(tr);
    });

    resultsList.appendChild(table);

});