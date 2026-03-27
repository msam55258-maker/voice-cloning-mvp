/**
 * app.js — Voice Cloning MVP · Controller Layer
 * ───────────────────────────────────────────
 * Coordinates between UI (ui.js) and API (api.js).
 * Handles authentication and the main lifecycle flow.
 */

// ── 1. GLOBAL STATE ──────────────────────────────────────────────────────────
const State = {
    voicePath:    null,
    audioUrl:     null,
    isGenerating: false,
    elapsed:      0,
    timers:       { elapsed: null, phase: null }
};

const GEN_PHASES = ['Analyzing voice embedding…', 'Generating spectrograms…', 'Synthesizing waveform…', 'Finalizing audio…'];

// ── 2. AUTHENTICATION ────────────────────────────────────────────────────────
const firebaseConfig = { apiKey: 'YOUR_API_KEY', authDomain: 'your-app-firebaseapp.com', projectId: 'your-project-id' };
const AUTH_MOCKED = firebaseConfig.apiKey === 'YOUR_API_KEY';
if (!AUTH_MOCKED) firebase.initializeApp(firebaseConfig);

async function loginWithGoogle() {
    const btn = document.getElementById('googleLoginBtn');
    if (btn) btn.disabled = true;

    try {
        if (AUTH_MOCKED) {
            await new Promise(r => setTimeout(r, 700));
            sessionStorage.setItem('userName', 'Dev User (Mocked)');
        } else {
            const provider = new firebase.auth.GoogleAuthProvider();
            const result = await firebase.auth().signInWithPopup(provider);
            sessionStorage.setItem('userName', result.user.displayName || 'User');
        }
        window.location.href = 'dashboard.html';
    } catch (e) {
        if (btn) btn.disabled = false;
        alert('Login failed: ' + e.message);
    }
}

// ── 3. DASHBOARD FLOW ────────────────────────────────────────────────────────
if (window.location.pathname.endsWith('dashboard.html')) {
    window.addEventListener('DOMContentLoaded', initDashboard);
}

async function initDashboard() {
    const user = sessionStorage.getItem('userName');
    if (!user) { window.location.href = 'index.html'; return; }
    document.getElementById('userNameBadge').textContent = user;

    // Listeners
    UI.elements.voiceFile = () => document.getElementById('voiceFile'); // add to elements
    UI.elements.voiceFile().addEventListener('change', e => { if (e.target.files[0]) handleUpload(e.target.files[0]); });
    UI.elements.scriptText().addEventListener('input', onScriptInput);
    initDragDrop();

    // Health
    try {
        const h = await API.checkHealth();
        UI.setStatus('serverLabel', h.data.model_loaded ? 'Backend ready' : 'Model loading…', h.data.model_loaded ? 'success' : 'warn');
        document.getElementById('serverDot').className = `server-dot server-${h.data.model_loaded ? 'online' : 'warn'}`;
    } catch {
        UI.setStatus('serverLabel', 'Backend offline', 'error');
        document.getElementById('serverDot').className = 'server-dot server-offline';
    }
}

// ── 4. UPLOAD LOGIC ──────────────────────────────────────────────────────────
async function handleUpload(file) {
    if (!file.name.toLowerCase().endsWith('.wav')) return UI.showToast('Only .wav supported', 'error');
    
    UI.setDropZoneState('uploading', file.name);
    try {
        const data = await API.uploadVoice(file);
        State.voicePath = data.voice_path;
        UI.setDropZoneState('success', `✓ ${file.name} (${data.duration_seconds}s)`);
        UI.markStepDone(1);
        UI.unlockStep(2);
        UI.showToast('Voice uploaded!', 'success');
        validateGen();
    } catch (e) {
        UI.setDropZoneState('error');
        UI.showToast(e.message, 'error');
    }
}

// ── 5. GENERATION LOGIC ──────────────────────────────────────────────────────
async function generateAudio() {
    const text = UI.elements.scriptText().value.trim();
    if (!text || !State.voicePath || State.isGenerating) return;

    State.isGenerating = true;
    UI.setGeneratingUI(true);
    startTimers();

    try {
        const data = await API.generateAudio(text, State.voicePath);
        State.audioUrl = `http://localhost:8000${data.audio_url}`;
        
        // Show output
        const player = UI.elements.audioPlayer();
        player.src = State.audioUrl;
        UI.elements.outputMeta().textContent = `Generated in ${data.processing_time_seconds}s`;
        UI.elements.outputSection().style.display = 'block';
        UI.markStepDone(3);
        UI.showToast('Audio ready!', 'success');
    } catch (e) {
        UI.showToast(e.message, 'error');
    } finally {
        stopTimers();
        State.isGenerating = false;
        UI.setGeneratingUI(false);
    }
}

// ── 6. HELPERS ───────────────────────────────────────────────────────────────
function onScriptInput() {
    const len = this.value.length;
    UI.elements.charCount().textContent = `${len} / 500`;
    validateGen();
}

function validateGen() {
    const len = UI.elements.scriptText().value.length;
    const canGen = State.voicePath && len >= 10 && len <= 500;
    UI.elements.generateBtn().disabled = !canGen;
    if (canGen) UI.unlockStep(3);
}

function startTimers() {
    State.elapsed = 0;
    State.timers.elapsed = setInterval(() => {
        State.elapsed++;
        UI.elements.loadingTimer().textContent = `${State.elapsed}s elapsed`;
    }, 1000);
    let pIdx = 0;
    UI.elements.loadingPhase().textContent = GEN_PHASES[0];
    State.timers.phase = setInterval(() => {
        pIdx = (pIdx + 1) % GEN_PHASES.length;
        UI.elements.loadingPhase().textContent = GEN_PHASES[pIdx];
    }, 12000);
}

function stopTimers() { clearInterval(State.timers.elapsed); clearInterval(State.timers.phase); }

function initDragDrop() {
    const zone = UI.elements.dropZone();
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', e => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        if (e.dataTransfer.files[0]) handleUpload(e.dataTransfer.files[0]);
    });
}

function downloadAudio() {
    if (!State.audioUrl) return;
    const a = document.createElement('a');
    a.href = State.audioUrl;
    a.download = 'voice_clone.wav';
    a.click();
}

function resetForNewGeneration() {
    UI.elements.outputSection().style.display = 'none';
}
