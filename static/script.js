// Animal Detection System - REST API integration

console.log("Animal Detection System Loaded");

// ---------------- HELPERS ----------------

function getToken() { return localStorage.getItem("ad_token"); }
function saveToken(t) { localStorage.setItem("ad_token", t); }
function removeToken() { localStorage.removeItem("ad_token"); }

function getRefreshToken() { return localStorage.getItem("ad_refresh_token"); }
function saveRefreshToken(t) { localStorage.setItem("ad_refresh_token", t); }
function removeRefreshToken() { localStorage.removeItem("ad_refresh_token"); }

const path = window.location.pathname;
if (!getToken() && path !== '/login' && path !== '/register') {
    window.location.href = '/login';
}

function showMessage(elementId, text, type) {

    const el = document.getElementById(elementId);

    if (!el) return;

    el.innerHTML = `<p style="color:${type === "error" ? "#f87171" : "#4ade80"}; margin-bottom:15px;">${text}</p>`;
}


async function apiRequest(url, options = {}) {

    const headers = options.headers || {};
    const token = getToken();
    
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        const refresh = getRefreshToken();
        if (refresh && url !== "/api/refresh") {
            const refreshRes = await fetch("/api/refresh", {
                method: "POST",
                headers: { "Authorization": `Bearer ${refresh}` }
            });
            if (refreshRes.ok) {
                const refreshData = await refreshRes.json();
                if (refreshData.success && refreshData.token) {
                    saveToken(refreshData.token);
                    headers["Authorization"] = `Bearer ${refreshData.token}`;
                    const retryRes = await fetch(url, { ...options, headers });
                    let retryData = null;
                    try { retryData = await retryRes.json(); } catch(e) {}
                    return { ok: retryRes.ok, status: retryRes.status, data: retryData };
                }
            }
        }
        removeToken();
        removeRefreshToken();
        window.location.href = "/login";
        return { ok: false, status: 401, data: null };
    }

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

            saveToken(data.token);
            if (data.refresh_token) {
                saveRefreshToken(data.refresh_token);
            }
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
            if (list) list.innerHTML = "";

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
        html += `<tr><td><a href="/uploads/${d.image}" target="_blank" style="color: inherit; text-decoration: none; cursor: pointer;">${d.image}</a></td><td>${d.animal}</td><td>${d.confidence}</td><td>${d.status}</td><td>${d.time}</td></tr>`;
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
let webcamStream = null;
let webcamTimer = null;
let isProcessingFrame = false;
let lastBoxes = [];   // Latest YOLO detections — updated every 1s

// Color map for labels
const LABEL_COLORS = {
    person: "#ff4444",
    cat: "#44aaff", dog: "#44aaff",
    bird: "#ffaa00", horse: "#ffaa00", cow: "#ffaa00",
    sheep: "#aa44ff", elephant: "#aa44ff", bear: "#aa44ff",
    zebra: "#00ffaa", giraffe: "#00ffaa"
};
function colorFor(label) { return LABEL_COLORS[label.toLowerCase()] || "#00ff00"; }

// Draws the current YOLO boxes onto the overlay canvas
function drawBoxes(canvas) {
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const W = canvas.width, H = canvas.height;

    for (const b of lastBoxes) {
        const x = b.x1 * W, y = b.y1 * H;
        const w = (b.x2 - b.x1) * W, h = (b.y2 - b.y1) * H;
        const color = colorFor(b.label);

        // Box
        ctx.strokeStyle = color;
        ctx.lineWidth = 2.5;
        ctx.strokeRect(x, y, w, h);

        // Label background
        const label = `${b.label} ${Math.round(b.conf * 100)}%`;
        ctx.font = "bold 13px Inter, Arial, sans-serif";
        const tw = ctx.measureText(label).width;
        const ty = y > 22 ? y - 22 : y + h;
        ctx.fillStyle = color;
        ctx.fillRect(x - 1, ty, tw + 10, 20);

        // Label text
        ctx.fillStyle = "#000";
        ctx.fillText(label, x + 4, ty + 14);
    }
}

async function toggleWebcam() {
    const card   = document.getElementById("webcamCard");
    const video  = document.getElementById("webcamVideo");
    const canvas = document.getElementById("webcamCanvas");

    if (!card || !video || !canvas) return;

    // ---- STOP ----
    if (webcamRunning) {
        webcamRunning = false;
        clearInterval(webcamTimer);
        if (webcamStream) webcamStream.getTracks().forEach(t => t.stop());
        video.srcObject = null;
        lastBoxes = [];
        canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
        card.style.display = "none";
        return;
    }

    // ---- START ----
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({ video: true });
    } catch (e) {
        alert("Camera permission denied. Please allow camera access in your browser.");
        return;
    }

    // <video> renders the live feed natively at full FPS — zero JS overhead
    video.srcObject = webcamStream;
    video.play();
    card.style.display = "block";
    webcamRunning = true;

    // Wait for real dimensions
    await new Promise(resolve => {
        if (video.videoWidth > 0) { resolve(); return; }
        video.addEventListener("loadedmetadata", resolve, { once: true });
    });

    canvas.width  = video.videoWidth;
    canvas.height = video.videoHeight;

    // Off-screen capture canvas
    const capture = document.createElement("canvas");
    capture.width  = video.videoWidth;
    capture.height = video.videoHeight;
    const captureCtx = capture.getContext("2d");

    // Every 1s: send a frame → get JSON boxes → redraw overlay
    // The <video> element keeps playing smoothly regardless
    webcamTimer = setInterval(async () => {
        if (!webcamRunning || isProcessingFrame || video.paused || video.readyState < 2) return;
        isProcessingFrame = true;

        captureCtx.drawImage(video, 0, 0, capture.width, capture.height);
        capture.toBlob(async (blob) => {
            if (!blob || !webcamRunning) { isProcessingFrame = false; return; }

            const fd = new FormData();
            fd.append("image", blob, "frame.jpg");

            try {
                const res = await fetch("/api/detect_frame", {
                    method: "POST",
                    body: fd,
                    headers: { "Authorization": "Bearer " + (getToken() || "") }
                });
                if (res.ok) {
                    const data = await res.json();
                    lastBoxes = data.boxes || [];
                    drawBoxes(canvas);
                }
            } catch(e) { /* skip */ }
            finally { isProcessingFrame = false; }

        }, "image/jpeg", 0.6); // 60% quality — only used for YOLO input, never displayed

    }, 1000);
}

function handleLogout() {
    removeToken();
    removeRefreshToken();
    window.location.href = "/login";
}



