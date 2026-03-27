/**
 * ui.js — Voice Cloning MVP · UI Layer
 * ───────────────────────────────────────────
 * All DOM manipulation, state transitions, and feedback components lived here.
 */

const UI = {
    // ── Elements ─────────────────────────────────────────────────────────────
    elements: {
        dropZone:      () => document.getElementById('dropZone'),
        dropIcon:      () => document.getElementById('dropIcon'),
        dropMain:      () => document.getElementById('dropMainText'),
        uploadProgress:() => document.getElementById('uploadProgress'),
        uploadFill:    () => document.getElementById('uploadFill'),
        uploadLabel:   () => document.getElementById('uploadLabel'),
        uploadStatus:  () => document.getElementById('uploadStatus'),
        scriptText:    () => document.getElementById('scriptText'),
        charCount:     () => document.getElementById('charCount'),
        scriptWarning: () => document.getElementById('scriptWarning'),
        generateBtn:   () => document.getElementById('generateBtn'),
        generateHint:  () => document.getElementById('generateHint'),
        loadingCard:   () => document.getElementById('loadingCard'),
        loadingPhase:  () => document.getElementById('loadingPhase'),
        loadingTimer:  () => document.getElementById('loadingTimer'),
        outputSection: () => document.getElementById('outputSection'),
        audioPlayer:   () => document.getElementById('audioPlayer'),
        outputMeta:    () => document.getElementById('outputMeta'),
    },

    // ── Toasts ───────────────────────────────────────────────────────────────
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const icons = {
            success: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
            error:   `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>`,
            info:    `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/></svg>`,
        };

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `${icons[type] || ''}<span>${message}</span>`;

        container.appendChild(toast);
        requestAnimationFrame(() => toast.classList.add('toast-in'));

        setTimeout(() => {
            toast.classList.remove('toast-in');
            toast.addEventListener('transitionend', () => toast.remove(), { once: true });
        }, 4000);
    },

    // ── Step State ───────────────────────────────────────────────────────────
    markStepDone(stepNum) {
        document.getElementById(`track${stepNum}`)?.classList.add('done');
        const check = document.getElementById(`stepCheck${stepNum}`);
        if (check) {
            check.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="var(--success)" stroke-width="2.5"
                stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/></svg>`;
        }
    },

    unlockStep(stepNum) {
        const ids = { 2: 'sectionScript', 3: 'sectionGenerate' };
        const sec = document.getElementById(ids[stepNum]);
        if (!sec) return;
        sec.classList.remove('section-locked');
        sec.removeAttribute('aria-disabled');
        sec.querySelectorAll('input, textarea, button').forEach(el => {
            if (el.id !== 'generateBtn') el.disabled = false;
        });
        document.getElementById(`track${stepNum}`)?.classList.add('active');
    },

    // ── Loaders ──────────────────────────────────────────────────────────────
    setDropZoneState(state, filename = '') {
        const zone = this.elements.dropZone();
        const icon = this.elements.dropIcon();
        const main = this.elements.dropMain();
        if (!zone || !icon) return;

        zone.className = `drop-zone dz-${state}`;
        if (filename) main.textContent = filename;

        const icons = {
            upload:  `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>`,
            success: `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
            error:   `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--error)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
            loading: `<div class="spinner-ring" style="width:32px;height:32px;"></div>`
        };
        icon.innerHTML = icons[state === 'uploading' ? 'loading' : state] || icons.upload;
    },

    setStatus(id, text, type = 'muted') {
        const el = document.getElementById(id);
        if (el) { el.textContent = text; el.className = `status-row status-${type}`; }
    },

    setGeneratingUI(isGenerating, phases = []) {
        const btn  = this.elements.generateBtn();
        const card = this.elements.loadingCard();
        const out  = this.elements.outputSection();
        if (isGenerating) {
            btn.disabled = true;
            btn.innerHTML = `<div class="spinner-sm"></div> Generating…`;
            card.style.display = 'block';
            out.style.display = 'none';
        } else {
            btn.innerHTML = `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg> Generate Audio`;
            card.style.display = 'none';
        }
    }
};

window.UI = UI;
