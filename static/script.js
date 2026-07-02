// Animal Detection System - REST API integration

console.log("Animal Detection System Loaded");

// ---------------- HELPERS ----------------

function showMessage(elementId, text, type) {

    const el = document.getElementById(elementId);

    if (!el) return;

    el.innerHTML = `<p style="color:${type === "error" ? "#f87171" : "#4ade80"}; margin-bottom:15px;">${text}</p>`;
}

async function apiRequest(url, options = {}) {

    const response = await fetch(url, {
        credentials: "same-origin",
        ...options
    });

    let data = null;

    try {
        data = await response.json();
    } catch (err) {
        data = null;
    }

    return { ok: response.ok, status: response.status, data };
}

// ---------------- LOGIN ----------------

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const btn = document.getElementById("loginBtn");
        btn.disabled = true;
        btn.textContent = "Logging in...";

        const { ok, data } = await apiRequest("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        btn.disabled = false;
        btn.textContent = "Login";

        if (ok && data && data.success) {

            showMessage("loginMessage", "Login successful. Redirecting...", "success");

            window.location.href = "/";

        } else {

            showMessage("loginMessage", (data && data.message) || "Login failed.", "error");

        }

    });

}

// ---------------- REGISTER ----------------

const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        const btn = document.getElementById("registerBtn");
        btn.disabled = true;
        btn.textContent = "Registering...";

        const { ok, data } = await apiRequest("/api/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });

        btn.disabled = false;
        btn.textContent = "Register";

        if (ok && data && data.success) {

            showMessage("registerMessage", "Account created. Redirecting to login...", "success");

            setTimeout(() => window.location.href = "/login", 1200);

        } else {

            showMessage("registerMessage", (data && data.message) || "Registration failed.", "error");

        }

    });

}

// ---------------- UPLOAD ----------------

const uploadForm = document.getElementById("uploadForm");

if (uploadForm) {

    uploadForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const filesInput = document.getElementById("imagesInput");

        if (!filesInput.files.length) {
            showMessage("uploadMessage", "Please choose at least one image.", "error");
            return;
        }

        const formData = new FormData();

        for (const file of filesInput.files) {
            formData.append("images", file);
        }

        const btn = document.getElementById("uploadBtn");
        btn.disabled = true;
        btn.textContent = "Uploading...";

        const { ok, data } = await apiRequest("/api/upload", {
            method: "POST",
            body: formData
        });

        btn.disabled = false;
        btn.textContent = "Upload Images";

        if (ok && data && data.success) {

            showMessage("uploadMessage", `Uploaded ${data.uploaded.length} image(s) successfully.`, "success");

            const list = document.getElementById("uploadedList");

            list.innerHTML = "<ul>" + data.uploaded.map(u => `<li>${u.filename}</li>`).join("") + "</ul>";

            uploadForm.reset();

            loadHistory();

        } else {

            showMessage("uploadMessage", (data && data.message) || "Upload failed.", "error");

        }

    });

}

// ---------------- DETECT ----------------

const detectBtn = document.getElementById("detectBtn");

if (detectBtn) {

    detectBtn.addEventListener("click", async function () {

        detectBtn.disabled = true;
        detectBtn.textContent = "Detecting...";

        showMessage("detectMessage", "Running YOLO detection, please wait...", "success");

        const { ok, data } = await apiRequest("/api/detect", {
            method: "GET"
        });

        detectBtn.disabled = false;
        detectBtn.textContent = "Detect Animals";

        if (ok && data && !data.message) {

            showMessage("detectMessage", "Detection complete.", "success");

            renderDetectionResults(data.detections);
            renderAnimalCount(data.animal_count);
            renderSummary(data.summary);
            renderGraph(data.graph);

        } else {

            showMessage("detectMessage", (data && data.message) || "Detection failed.", "error");

        }

    });

}

function renderDetectionResults(detections) {

    const container = document.getElementById("detectionResultsContainer");

    if (!detections || detections.length === 0) {
        container.innerHTML = "<p>No detections available.</p>";
        return;
    }

    let html = "<table><tr><th>Image</th><th>Animal</th><th>Confidence</th><th>Status</th><th>Inference Time</th></tr>";

    detections.forEach(d => {
        html += `<tr><td>${d.image}</td><td>${d.animal}</td><td>${d.confidence}</td><td>${d.status}</td><td>${d.time}</td></tr>`;
    });

    html += "</table>";

    container.innerHTML = html;

}

function renderAnimalCount(animalCount) {

    const container = document.getElementById("animalCountContainer");

    const entries = animalCount ? Object.entries(animalCount) : [];

    if (entries.length === 0) {
        container.innerHTML = "<p>No animal count available.</p>";
        return;
    }

    let html = "<table><tr><th>Animal</th><th>Count</th></tr>";

    entries.forEach(([animal, count]) => {
        html += `<tr><td>${animal}</td><td>${count}</td></tr>`;
    });

    html += "</table>";

    container.innerHTML = html;

}

function renderSummary(summary) {

    const container = document.getElementById("summaryContainer");

    if (!summary) {
        container.innerHTML = "<p>No summary available.</p>";
        return;
    }

    container.innerHTML = `
        <table>
            <tr><th>Total Images Processed</th><td>${summary.images}</td></tr>
            <tr><th>Total Animals Detected</th><td>${summary.animals}</td></tr>
            <tr><th>Unique Animal Types</th><td>${summary.unique}</td></tr>
            <tr><th>Average Confidence</th><td>${summary.confidence}</td></tr>
            <tr><th>Average Inference Time</th><td>${summary.time}</td></tr>
        </table>
    `;

}

function renderGraph(graph) {

    const container = document.getElementById("graphContainer");

    if (!graph) {
        container.innerHTML = "<p>No graph available.</p>";
        return;
    }

    container.innerHTML = `<img src="${graph}?t=${Date.now()}" alt="Detection Graph" style="width:100%; max-width:800px; display:block; margin:auto; border-radius:10px;">`;

}

// ---------------- HISTORY ----------------

async function loadHistory() {

    const container = document.getElementById("historyContainer");

    if (!container) return;

    const { ok, data } = await apiRequest("/api/history", { method: "GET" });

    if (!ok || !data || data.length === 0) {
        container.innerHTML = "<p>No upload history available.</p>";
        return;
    }

    let html = "<table><tr><th>Image</th><th>Uploaded At</th><th>Action</th></tr>";

    data.forEach(item => {
        html += `<tr>
            <td>${item.ImageName}</td>
            <td>${item.UploadedAt}</td>
            <td><button onclick="deleteImage(${item.ImageID})">Delete</button></td>
        </tr>`;
    });

    html += "</table>";

    container.innerHTML = html;

}

async function deleteImage(imageId) {

    const { ok, data } = await apiRequest(`/api/image/${imageId}`, { method: "DELETE" });

    if (ok) {
        loadHistory();
    } else {
        alert((data && data.message) || "Failed to delete image.");
    }

}

if (document.getElementById("historyContainer")) {
    loadHistory();
}

const clearHistoryBtn = document.getElementById("clearHistoryBtn");

if (clearHistoryBtn) {

    clearHistoryBtn.addEventListener("click", async function () {

        const confirmed = confirm("This will permanently delete all uploaded images and detection results. Continue?");

        if (!confirmed) return;

        clearHistoryBtn.disabled = true;
        clearHistoryBtn.textContent = "Clearing...";

        const { ok, data } = await apiRequest("/api/history", { method: "DELETE" });

        clearHistoryBtn.disabled = false;
        clearHistoryBtn.textContent = "🗑️ Clear All History";

        if (ok && data && data.success) {

            showMessage("historyMessage", data.message, "success");
            loadHistory();

        } else {

            showMessage("historyMessage", (data && data.message) || "Failed to clear history.", "error");

        }

    });

}

const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");

if (refreshHistoryBtn) {

    refreshHistoryBtn.addEventListener("click", loadHistory);

}

// ---------------- WEBCAM ----------------

let webcamRunning = false;

function toggleWebcam() {

    const card = document.getElementById("webcamCard");
    const img = document.getElementById("webcamFeed");

    if (!card || !img) return;

    if (!webcamRunning) {

        img.src = "/video_feed";
        card.style.display = "block";
        webcamRunning = true;

    } else {

        img.src = "";
        card.style.display = "none";
        webcamRunning = false;

    }

}
