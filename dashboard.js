// --- Extension 1: Multi-Rack Fleet Facility Switcher Topologies ---
const FLEET_RACKS = {
    "RACK_ALPHA_01": [
        { id: "CELL_01", soh: 96.3, temp: 25.0, status: "healthy" },
        { id: "CELL_02", soh: 92.8, temp: 27.3, status: "healthy" },
        { id: "CELL_03", soh: 88.2, temp: 36.1, status: "warning" },
        { id: "CELL_04", soh: 96.1, temp: 24.8, status: "healthy" },
        { id: "CELL_05", soh: 95.5, temp: 25.7, status: "healthy" },
        { id: "CELL_06", soh: 94.5, temp: 26.7, status: "healthy" },
        { id: "CELL_07", soh: 76.5, temp: 48.2, status: "critical" }, // Critical hot-spot
        { id: "CELL_08", soh: 95.3, temp: 26.8, status: "healthy" },
        { id: "CELL_09", soh: 93.7, temp: 26.9, status: "healthy" },
        { id: "CELL_10", soh: 92.4, temp: 27.2, status: "healthy" },
        { id: "CELL_11", soh: 94.2, temp: 27.5, status: "healthy" },
        { id: "CELL_12", soh: 88.2, temp: 36.1, status: "warning" },
        { id: "CELL_13", soh: 95.2, temp: 25.8, status: "healthy" },
        { id: "CELL_14", soh: 92.8, temp: 25.9, status: "healthy" },
        { id: "CELL_15", soh: 96.6, temp: 24.9, status: "healthy" },
        { id: "CELL_16", soh: 94.5, temp: 25.6, status: "healthy" }
    ],
    "RACK_BETA_02": Array.from({ length: 16 }, (_, i) => ({
        id: `CELL_${String(i + 1).padStart(2, '0')}`,
        soh: i > 10 ? 78.4 : 86.2,
        temp: i > 10 ? 39.5 : 29.1,
        status: i > 10 ? "warning" : "healthy"
    })),
    "RACK_GAMMA_03": Array.from({ length: 16 }, (_, i) => ({
        id: `CELL_${String(i + 1).padStart(2, '0')}`,
        soh: 98.5,
        temp: 23.5,
        status: "healthy"
    }))
};

function switchFacilityRack(rackId) {
    const gridContainer = document.getElementById("rack-grid-container");
    const cells = FLEET_RACKS[rackId] || FLEET_RACKS["RACK_ALPHA_01"];
    
    gridContainer.innerHTML = "";
    cells.forEach(cell => {
        const tile = document.createElement("div");
        tile.className = `cell-tile ${cell.status}`;
        tile.onclick = () => {
            document.getElementById("battery_id").value = cell.id;
            document.getElementById("avg_temp_c").value = cell.temp;
            document.getElementById("capacity_ah").value = ((cell.soh / 100) * 2.0).toFixed(2);
            executeInference();
        };
        tile.innerHTML = `
            <div class="fw-bold extra-small text-light">${cell.id}</div>
            <div class="extra-small text-info">${cell.soh}%</div>
            <div class="extra-small text-muted-custom">${cell.temp}°C</div>
        `;
        gridContainer.appendChild(tile);
    });
}

// --- Extension 2: Functional PDF Diagnostic Report Exporter ---
function downloadPdfReport() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const currentSoh = document.getElementById("soh-display")?.innerText || "92.00%";
    const currentRul = document.getElementById("rul-display")?.innerText || "883 Cycles";
    const netArbitrage = document.getElementById("net-arbitrage-disp")?.innerText || "+$22.92";

    // Title & Header
    doc.setFillColor(11, 15, 25);
    doc.rect(0, 0, 210, 297, "F");
    doc.setTextColor(14, 165, 233);
    doc.setFontSize(20);
    doc.text("BESS Battery Diagnostic & Analytics Report", 14, 22);

    doc.setFontSize(10);
    doc.setTextColor(148, 163, 184);
    doc.text(`Generated On: ${new Date().toLocaleString()}`, 14, 30);
    doc.text(`Facility Rack: ${document.getElementById("rack-selector")?.value || "RACK_ALPHA_01"}`, 14, 36);

    // Divider
    doc.setDrawColor(34, 45, 69);
    doc.line(14, 42, 196, 42);

    // Key Health Metrics
    doc.setFontSize(14);
    doc.setTextColor(255, 255, 255);
    doc.text("1. Executive System Diagnostics", 14, 52);

    doc.setFontSize(11);
    doc.setTextColor(203, 213, 225);
    doc.text(`• State of Health (SOH): ${currentSoh}`, 20, 62);
    doc.text(`• Remaining Useful Life (RUL): ${currentRul}`, 20, 70);
    doc.text(`• System Net Arbitrage Margin: ${netArbitrage}`, 20, 78);

    // Anomaly Section
    doc.setFontSize(14);
    doc.setTextColor(239, 68, 68);
    doc.text("2. Anomaly & Critical Thermal Audit", 14, 94);

    doc.setFontSize(10);
    doc.setTextColor(203, 213, 225);
    doc.text("• Target Unit: CELL_07 (Hot-spot breach detected)", 20, 104);
    doc.text("• Max Operating Temp: 48.2°C (Threshold: 45.0°C)", 20, 112);
    doc.text("• Root Cause: High ambient operating temp during fast-charging.", 20, 120);
    doc.text("• Action: Engage HVAC cooling and restrict C-rate to 1.0C.", 20, 128);

    // Save File
    doc.save(`BESS_Diagnostic_Report_${Date.now()}.pdf`);
}

// --- Extension 3: Automated Root Cause Analysis (RCA) Assistant ---
function populateRcaModal(cellId, temp, score) {
    document.getElementById("rca-cell-id").innerText = cellId;
    document.getElementById("rca-temp").innerText = `${temp}°C`;
    document.getElementById("rca-score").innerText = `${score} / 1.0`;

    document.getElementById("rca-findings-text").innerHTML = `
        Cell <strong>${cellId}</strong> thermal degradation is driven by sustained operating temperature 
        (<strong>${temp}°C</strong>) exceeding the critical alert threshold. 
        High internal resistance spikes combined with rapid charge cycles have accelerated localized capacity loss.
    `;
}

// Initialise Rack View on DOM Load
document.addEventListener("DOMContentLoaded", () => {
    switchFacilityRack("RACK_ALPHA_01");
});