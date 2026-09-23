let degradationChart = null;
let shapChart = null;

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Trajectory Chart with What-If Dataset
    const ctxDeg = document.getElementById("degradationChart");
    if (ctxDeg) {
        degradationChart = new Chart(ctxDeg.getContext("2d"), {
            type: "line",
            data: {
                labels: [],
                datasets: [
                    {
                        label: "Historical Capacity (Ah)",
                        data: [],
                        borderColor: "#0ea5e9",
                        backgroundColor: "rgba(14, 165, 233, 0.15)",
                        borderWidth: 2,
                        fill: true,
                        tension: 0.2,
                        pointRadius: 2
                    },
                    {
                        label: "Current Trajectory",
                        data: [],
                        borderColor: "#eab308",
                        borderDash: [5, 5],
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3,
                        pointRadius: 0
                    },
                    {
                        label: "Optimized What-If Trajectory",
                        data: [],
                        borderColor: "#22c55e",
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3,
                        pointRadius: 0
                    },
                    {
                        label: "95% Upper CI",
                        data: [],
                        borderColor: "rgba(34, 197, 94, 0.15)",
                        borderWidth: 1,
                        borderDash: [2, 2],
                        pointRadius: 0,
                        fill: false
                    },
                    {
                        label: "95% Confidence Band",
                        data: [],
                        borderColor: "rgba(34, 197, 94, 0.15)",
                        borderWidth: 1,
                        borderDash: [2, 2],
                        pointRadius: 0,
                        fill: "-1",
                        backgroundColor: "rgba(34, 197, 94, 0.10)"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: "Battery Operating Cycles", color: "#94a3b8", font: { size: 10 } },
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#94a3b8", font: { size: 10 } }
                    },
                    y: {
                        title: { display: true, text: "Capacity (Ah)", color: "#94a3b8", font: { size: 10 } },
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#94a3b8", font: { size: 10 } }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: "#f1f5f9",
                            font: { size: 10 },
                            filter: (item) => !item.text.includes("Upper CI")
                        }
                    }
                }
            }
        });
        window.myDegradationChart = degradationChart;
    }

    // 2. Initialize SHAP Feature Importance Bar Chart
    const ctxShap = document.getElementById("shapChart");
    if (ctxShap) {
        shapChart = new Chart(ctxShap.getContext("2d"), {
            type: "bar",
            data: {
                labels: ["Internal Resistance", "Operating Temp", "Capacity Loss", "Peak Voltage"],
                datasets: [{
                    label: "RUL Cycle Reduction",
                    data: [42.5, 28.1, 18.4, 12.2],
                    backgroundColor: ["#f43f5e", "#fb923c", "#38bdf8", "#a855f7"],
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: "|Δ RUL Impact (Cycles)|", color: "#38bdf8", font: { size: 10, weight: "bold" } },
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#94a3b8", font: { size: 9 }, callback: (v) => `-${v} cyc` }
                    },
                    y: { grid: { display: false }, ticks: { color: "#f1f5f9", font: { size: 10 } } }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` -${ctx.raw} Cycles RUL degradation due to ${ctx.label}`
                        }
                    }
                }
            }
        });
        window.myShapChart = shapChart;
    }

    window.updateTrajectoryChart(150, 1.84, 883, 1050, 2.0);
});

// Trajectory Update Function
window.updateTrajectoryChart = (currentCycle, currentCapacity, predictedRul, optimizedRul = null, nominalCapacity = 2.0) => {
    if (!window.myDegradationChart) return;

    const eolCapacity = nominalCapacity * 0.8;
    const integerRUL = Math.max(1, Math.round(predictedRul));
    const optRUL = optimizedRul ? Math.max(integerRUL, Math.round(optimizedRul)) : integerRUL;

    const labels = [];
    const historicalData = [];
    const currentTrajectory = [];
    const optimizedTrajectory = [];
    const upperCI = [];
    const lowerCI = [];

    const histSteps = 6;
    const stepSize = Math.max(1, Math.floor(currentCycle / histSteps));

    for (let c = 0; c < currentCycle; c += stepSize) {
        labels.push(`Cyl ${c}`);
        const cap = nominalCapacity - ((nominalCapacity - currentCapacity) * Math.pow(c / currentCycle, 0.85));
        historicalData.push(parseFloat(cap.toFixed(3)));
        currentTrajectory.push(null);
        optimizedTrajectory.push(null);
        upperCI.push(null);
        lowerCI.push(null);
    }

    labels.push(`Cyl ${currentCycle}`);
    historicalData.push(currentCapacity);
    currentTrajectory.push(currentCapacity);
    optimizedTrajectory.push(currentCapacity);
    upperCI.push(currentCapacity);
    lowerCI.push(currentCapacity);

    const maxProj = Math.max(integerRUL, optRUL);
    const projSteps = 8;
    const projStepSize = Math.max(1, Math.floor(maxProj / projSteps));

    for (let k = currentCycle + projStepSize; k <= currentCycle + maxProj; k += projStepSize) {
        labels.push(`Cyl ${k}`);
        historicalData.push(null);

        // Current trajectory
        const progCur = Math.min(1.0, (k - currentCycle) / integerRUL);
        const capCur = currentCapacity - ((currentCapacity - eolCapacity) * Math.pow(progCur, 1.35));
        currentTrajectory.push(progCur >= 1.0 ? eolCapacity : parseFloat(capCur.toFixed(3)));

        // Optimized trajectory
        const progOpt = Math.min(1.0, (k - currentCycle) / optRUL);
        const capOpt = currentCapacity - ((currentCapacity - eolCapacity) * Math.pow(progOpt, 1.35));
        optimizedTrajectory.push(parseFloat(capOpt.toFixed(3)));

        const ciUncertainty = (currentCapacity - eolCapacity) * 0.12 * Math.sqrt(progCur);
        upperCI.push(parseFloat((capCur + ciUncertainty).toFixed(3)));
        lowerCI.push(parseFloat((capCur - ciUncertainty).toFixed(3)));
    }

    window.myDegradationChart.data.labels = labels;
    window.myDegradationChart.data.datasets[0].data = historicalData;
    window.myDegradationChart.data.datasets[1].data = currentTrajectory;
    window.myDegradationChart.data.datasets[2].data = optimizedTrajectory;
    window.myDegradationChart.data.datasets[3].data = upperCI;
    window.myDegradationChart.data.datasets[4].data = lowerCI;

    window.myDegradationChart.options.scales.y.min = parseFloat((eolCapacity * 0.85).toFixed(2));
    window.myDegradationChart.options.scales.y.max = parseFloat((nominalCapacity * 1.08).toFixed(2));
    window.myDegradationChart.update();
};

window.updateShapChart = (shapObj) => {
    if (!window.myShapChart || !shapObj) return;
    window.myShapChart.data.labels = Object.keys(shapObj);
    window.myShapChart.data.datasets[0].data = Object.values(shapObj).map(v => Math.abs(parseFloat(v)));
    window.myShapChart.update();
};