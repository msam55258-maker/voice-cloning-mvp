/**
 * api.js — Voice Cloning MVP · API Client Layer
 * ───────────────────────────────────────────
 * Consolidates all fetch() calls to the backend in one place.
 * Returns only raw data or throws typed errors for app.js to handle.
 */

const API_BASE = 'http://localhost:8000';

const API = {
    /** Health check ping to see if server is up and model is loaded. */
    async checkHealth() {
        const r = await fetch(`${API_BASE}/`, { signal: AbortSignal.timeout(5000) });
        if (!r.ok) throw new Error('Backend unhealthy');
        return r.json();
    },

    /** Upload a voice sample (FormData). */
    async uploadVoice(file) {
        const fd = new FormData();
        fd.append('file', file);

        const r = await fetch(`${API_BASE}/upload-voice`, { method: 'POST', body: fd });
        const b = await r.json();
        if (!r.ok) throw new Error(b?.detail?.message || b?.detail || 'Upload failed');
        return b.data;
    },

    /** Synthesize speech from text. */
    async generateAudio(text, voicePath) {
        const r = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, voice_path: voicePath }),
        });
        const b = await r.json();
        if (!r.ok) throw new Error(b?.detail?.message || b?.detail || 'Generation failed');
        return b.data;
    }
};

window.API = API; // Expose globally
