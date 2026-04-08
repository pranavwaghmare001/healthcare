let currentUser = null;
let currentName = "";
let fetchedSymptoms = [];

document.addEventListener("DOMContentLoaded", async () => {
    document.getElementById('auth-container').classList.add('active');
    try {
        let res = await fetch('/api/symptoms');
        let data = await res.json();
        let sel = document.getElementById('diag-select');
        data.symptoms.forEach(s => {
            let opt = document.createElement('option');
            opt.value = s;
            opt.innerText = s.replace(/_/g, ' ').toUpperCase();
            sel.appendChild(opt);
        });
    } catch(e) {}
});

function switchAuthTab(tab) {
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(`${tab}-form`).classList.add('active');
    event.target.classList.add('active');
}

document.getElementById('login-form').onsubmit = async (e) => {
    e.preventDefault();
    const u = document.getElementById('login-user').value;
    const p = document.getElementById('login-pwd').value;
    
    try {
        let res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, password: p})
        });
        
        let data = await res.json();
        if(res.ok && data.success) {
            currentUser = data.user_id;
            currentName = data.full_name;
            enterDashboard();
        } else {
            document.getElementById('login-error').innerText = data.detail || "Invalid credentials.";
        }
    } catch (err) {
        document.getElementById('login-error').innerText = "Server offline.";
    }
}

document.getElementById('signup-form').onsubmit = async (e) => {
    e.preventDefault();
    const u = document.getElementById('signup-user').value;
    const p = document.getElementById('signup-pwd').value;
    const n = document.getElementById('signup-name').value;
    const a = document.getElementById('signup-age').value;
    
    try {
        let res = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, password: p, full_name: n, age: parseInt(a)})
        });
        
        if(res.ok) {
            alert("Patient Profile Deployed Successfully! Please log in.");
            switchAuthTab('login');
        } else {
            let err = await res.json();
            document.getElementById('signup-error').innerText = err.detail || "Registration failed.";
        }
    } catch(err) {
        document.getElementById('signup-error').innerText = "Server offline.";
    }
}

function enterDashboard() {
    document.getElementById('auth-container').classList.remove('active');
    document.getElementById('dashboard-container').style.display = 'flex';
    document.getElementById('welcome-msg').innerText = "👤 " + currentName;
}

function logout() {
    currentUser = null;
    document.getElementById('dashboard-container').style.display = 'none';
    document.getElementById('auth-container').classList.add('active');
}

function navigate(view) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(`view-${view}`).classList.add('active');
    
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    if(event && event.target.tagName === 'BUTTON') event.target.classList.add('active');
    
    if(view === 'history') fetchHistory();
}

async function extractSymptoms() {
    const txt = document.getElementById('diag-text').value;
    if(!txt.trim()) return;
    
    let res = await fetch('/api/extract_symptoms', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text: txt})
    });
    let data = await res.json();
    fetchedSymptoms = data.symptoms;
    
    let cont = document.getElementById('selected-symptoms');
    cont.innerHTML = "";
    if(fetchedSymptoms.length === 0) {
        cont.innerHTML = "<span style='color:var(--error)'>No valid medical vectors recognized. Try different synonyms or select below.</span>";
        return;
    }
    
    fetchedSymptoms.forEach(s => {
        let sp = document.createElement('span');
        sp.className = 'tag';
        sp.innerText = s;
        cont.appendChild(sp);
    });
}

async function runDiagnosis() {
    let manualOptions = Array.from(document.getElementById('diag-select').selectedOptions).map(o => o.value);
    let finalPayload = [...new Set([...fetchedSymptoms, ...manualOptions])];

    if(finalPayload.length === 0) return alert("You must extract symptoms first or manually select them from the list before deploying the AI scanner.");
    
    const age = document.getElementById('diag-age').value;
    const loc = document.getElementById('diag-loc').value;
    let d = document.getElementById('diag-results');
    d.innerHTML = "<p style='color:#3b82f6'>Computing predictive models...</p>";
    
    let res = await fetch('/api/diagnose', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_id: currentUser,
            symptoms: finalPayload,
            age: parseInt(age),
            location: loc || "Unknown"
        })
    });
    
    let data = await res.json();
    d.innerHTML = "";
    if(!data.success) { d.innerHTML = "<p>No matches found in the predictive models.</p>"; return; }
    
    if(data.is_emergency) {
        d.innerHTML += `<div class="card" style="border-color:var(--error); background:rgba(239, 68, 68, 0.1);">
            <h3 style="color:var(--error)">🚨 CRITICAL EMERGENCY ROUTING DETECTED</h3>
            <p>Triggering condition: ${data.critical_symptoms.join(', ')}</p>
            <button class="btn logout" style="width:100%; margin-top:1rem;">📞 DISPATCH AMBULANCE (108)</button>
        </div>`;
    }
    
    data.results.forEach((r, i) => {
        d.innerHTML += `
        <div class="card">
            <h3 style="color:var(--primary)">${i+1}. ${r.disease} - Probability: ${Math.round(r.probability)}%</h3>
            <p>Severity Vector: <span style="font-weight:bold">${r.severity}</span></p>
        </div>`;
    });
    
    d.innerHTML += `<div class="card"><h3>🏠 Home Action Protocol</h3><ul><li>${data.care_tips.diet}</li><li>${data.care_tips.remedies}</li></ul></div>`;
}

async function scanReport() {
    const file = document.getElementById('report-file').files[0];
    if(!file) return alert("Select a local file first.");
    
    let fd = new FormData();
    fd.append('user_id', currentUser);
    fd.append('file', file);
    
    let d = document.getElementById('report-results');
    d.innerHTML = "<p style='color:#3b82f6'>Spinning up Optical Character Recognition (OCR)...</p>";
    
    let res = await fetch('/api/reports/upload', {
        method: 'POST',
        body: fd
    });
    let data = await res.json();
    
    if(data.success) {
        d.innerHTML = `<div class="card"><h3 style="color:var(--primary)">Extracted Raw Biomarkers</h3><pre>${JSON.stringify(data.metrics, null, 2)}</pre></div>`;
    } else {
        d.innerHTML = `<p style="color:var(--error)">Error Code: ${data.error}</p>`;
    }
}

async function fetchHistory() {
    let res = await fetch(`/api/history/${currentUser}`);
    let data = await res.json();
    let d = document.getElementById('history-results');
    d.innerHTML = "";
    
    if(data.history.length === 0) {
        d.innerHTML = "<p>Timeline is empty. Trigger a diagnosis or OCR scan to synchronize history.</p>";
        return;
    }
    
    data.history.forEach(h => {
        d.innerHTML += `<div class="card" style="margin-top:1rem;">
            <p style="color:#94a3b8; font-size:0.9rem; font-weight:bold;">${h.time} | ${h.type.toUpperCase()}</p>
            <pre>${JSON.stringify(h.data, null, 2)}</pre>
        </div>`;
    });
}

async function sendChat() {
    let t = document.getElementById('chat-input').value;
    if(!t.trim()) return;
    let b = document.getElementById('chat-box');
    b.innerHTML += `<p><b>You:</b> ${t}</p>`;
    document.getElementById('chat-input').value = "";
    b.scrollTop = b.scrollHeight;
    
    let res = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: t})
    });
    let data = await res.json();
    
    b.innerHTML += `<p><b style="color:var(--primary)">AI Doctor:</b> ${data.response}</p>`;
    b.scrollTop = b.scrollHeight;
}
