# Voice Cloning MVP

A minimum viable product that lets a user sign in, upload a short voice sample, enter a text script, and generate speech audio that sounds like the uploaded voice — using XTTS v2 (Coqui TTS).

---

## 1. Project Overview

This project implements a complete voice cloning pipeline as a local web application.

**Core flow:**  
Login → Upload voice sample → Enter script → Generate cloned audio → Play / Download

The backend is built with **FastAPI** (Python) and the frontend with plain **HTML / CSS / JavaScript**. The AI model (**XTTS v2**) is loaded once at server startup and reused for every generation request.

---

## 2. System Flow

```
┌──────────┐     ┌──────────────┐     ┌───────────────┐     ┌────────────┐
│  Browser  │────▶│  Frontend    │────▶│  FastAPI       │────▶│  XTTS v2   │
│  (User)   │◀────│  (HTML/JS)   │◀────│  Backend       │◀────│  Model     │
└──────────┘     └──────────────┘     └───────────────┘     └────────────┘
                                            │    ▲
                                            ▼    │
                                      ┌──────────────┐
                                      │  Local Disk   │
                                      │  /voices/     │
                                      │  /outputs/    │
                                      └──────────────┘
```

**Step-by-step:**

1. User opens `index.html` and clicks **Login with Google** (Firebase Auth, or mock fallback for development).
2. After login, user is redirected to `dashboard.html`.
3. User uploads a `.wav` voice sample (drag-and-drop or file picker).
4. Frontend sends the file to `POST /upload-voice`. Backend validates the WAV header and duration, saves it to `/voices/`, and returns the file path.
5. User types a script (10–500 characters) and clicks **Generate Audio**.
6. Frontend sends text + voice path to `POST /generate`. Backend loads the voice embedding and synthesizes audio via XTTS v2, saving the result to `/outputs/`.
7. Backend returns the audio URL. Frontend displays the audio player with play and download options.

---

## 3. Features

- Google Sign-In via Firebase (with mock fallback for local development)
- WAV file upload with binary header validation and duration check
- Text-to-speech generation using a cloned voice
- Audio playback and direct `.wav` download
- Structured JSON responses on all endpoints
- Input validation, path-traversal protection, and centralized logging
- Drag-and-drop upload with visual feedback
- Step-by-step UI flow with section locking

---

## 4. Tech Stack

| Layer     | Technology                              |
|-----------|-----------------------------------------|
| Frontend  | HTML5, CSS3, Vanilla JavaScript         |
| Backend   | Python 3.9+, FastAPI, Pydantic v2       |
| AI Model  | Coqui TTS — XTTS v2, PyTorch           |
| Auth      | Firebase Authentication (Google)        |
| Storage   | Local filesystem (`/voices/`, `/outputs/`) |

---

## 5. Architecture Overview

The system is split into four clear layers:

### Frontend Layer
Three JavaScript files with distinct responsibilities:
- `api.js` — All `fetch()` calls to the backend (network layer)
- `ui.js` — All DOM manipulation, toasts, and visual state transitions (view layer)
- `app.js` — Coordinates between API and UI; handles auth and main flow (controller)

### Backend Layer
FastAPI application with modular structure:
- `routes/upload.py` — Handles voice file upload and validation
- `routes/generate.py` — Handles synthesis requests and serves output files
- `main.py` — Application entrypoint, CORS middleware, request logging

### AI Service Layer
- `services/tts_service.py` — Loads the XTTS v2 model once at startup, exposes a `synthesise()` function
- Model is kept in memory as a singleton to avoid repeated loading (~2 GB)

### Storage Layer
- `services/file_service.py` — All file I/O operations (save, delete, validate output)
- Each uploaded voice and generated audio gets a UUID filename to prevent overwrites

---

## 6. Folder Structure

```
project/
├── backend/
│   ├── main.py                 # Entrypoint, middleware, startup hooks
│   ├── config.py               # Settings from environment variables
│   ├── routes/
│   │   ├── upload.py           # POST /upload-voice
│   │   └── generate.py         # POST /generate, GET /outputs/{file}
│   ├── services/
│   │   ├── tts_service.py      # XTTS v2 model loading and synthesis
│   │   └── file_service.py     # File save, delete, validation
│   ├── models/
│   │   ├── request_models.py   # Pydantic input schemas
│   │   └── response_models.py  # Pydantic response schemas
│   ├── utils/
│   │   ├── validators.py       # WAV header check, duration, path safety
│   │   ├── responses.py        # ok() and fail() envelope helpers
│   │   └── logger.py           # Centralized logging config
│   ├── voices/                 # Uploaded voice samples
│   └── outputs/                # Generated audio files
├── frontend/
│   ├── index.html              # Landing page (login)
│   ├── dashboard.html          # Main workspace
│   ├── app.js                  # Controller (auth + flow)
│   ├── api.js                  # Network calls
│   ├── ui.js                   # DOM manipulation
│   └── styles.css              # Styling
├── requirements.txt
└── README.md
```

---

## 7. API Endpoints

All responses follow a consistent envelope format:

```json
{
  "status": "success | error",
  "message": "Human-readable description",
  "data": { }
}
```

### `POST /upload-voice`

Upload a WAV voice sample for cloning.

| Parameter | Type              | Description            |
|-----------|-------------------|------------------------|
| `file`    | `multipart/form-data` | WAV audio file (≤10 MB) |

**Success response (200):**
```json
{
  "status": "success",
  "message": "Voice sample uploaded successfully.",
  "data": {
    "voice_path": "backend/voices/voice_<uuid>.wav",
    "duration_seconds": 5.12
  }
}
```

### `POST /generate`

Generate speech audio from text using a previously uploaded voice.

| Parameter    | Type   | Description                        |
|-------------|--------|------------------------------------|
| `text`      | string | Script text (10–500 characters)    |
| `voice_path`| string | Path returned by `/upload-voice`   |

**Success response (200):**
```json
{
  "status": "success",
  "message": "Audio generated successfully.",
  "data": {
    "audio_url": "/outputs/audio_<uuid>.wav",
    "processing_time_seconds": 8.46
  }
}
```

### `GET /outputs/{filename}`

Serves a generated audio file for playback or download.

### `GET /`

Health check. Returns `{ "data": { "model_loaded": true } }`.

---

## 8. Design Decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI** | Native async support, automatic OpenAPI docs, and built-in Pydantic validation — ideal for a Python ML backend. |
| **Model loaded once at startup** | XTTS v2 weights are ~2 GB. Loading per-request would make each call take 30+ seconds longer. A singleton avoids this. |
| **Local file storage** | Simplest approach for an MVP. No external dependencies (S3, database). UUID filenames prevent collisions. |
| **Modular backend structure** | Routes, services, and utils are separated so each file has one clear responsibility. Makes the code easy to navigate and test. |
| **Frontend split (api/ui/app)** | Prevents a single monolithic JS file. API calls, DOM updates, and flow logic can each be understood independently. |
| **Mock auth fallback** | Allows the full flow to work locally without Firebase credentials. Real Firebase can be enabled by updating `firebaseConfig`. |
| **Environment variables for config** | All limits (file size, text length, model name) can be changed without editing code. See `config.py`. |

---

## 9. Error Handling & Stability

### Input Validation
- **WAV header check**: Reads the first 12 bytes for `RIFF` and `WAVE` magic bytes before accepting any upload.
- **Duration check**: Rejects audio shorter than 3 seconds (configurable via `MIN_AUDIO_DURATION_S`).
- **Text length**: Enforced at 10–500 characters via Pydantic field constraints.
- **File size**: Uploads exceeding 10 MB are rejected (configurable via `MAX_FILE_SIZE_MB`).

### Security
- **Path traversal protection**: All user-supplied file paths are resolved to absolute paths and checked against the allowed directory. Requests with `../` patterns are rejected.
- **Filename sanitization**: Output serving only accepts simple filenames — no slashes or `..` sequences.

### Structured Responses
- Every endpoint returns the same `{ status, message, data }` envelope.
- Errors use `HTTPException` with the same envelope shape inside `detail`, so the frontend always knows how to parse them.

### Logging
- HTTP middleware logs every request (method, path, status code, latency in ms).
- Service-level logging tracks model loading, file operations, and synthesis timing.
- All loggers use a centralized format defined in `utils/logger.py`.

### Graceful Failures
- If the TTS model fails to load at startup, the server still starts but returns `503` on generation requests.
- If synthesis fails mid-generation, the partial output file is cleaned up before returning an error.
- If a requested output file doesn't exist, the endpoint returns `404` with a clear message.

---

## 10. Setup Instructions

### Prerequisites
- Python 3.9 or higher
- `pip` package manager

### Step 1: Clone and set up

```bash
cd MVP_Voice_Cloning
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Start the backend

```bash
export COQUI_TOS_AGREED=1
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The first run will download the XTTS v2 model (~2 GB). Subsequent runs use the cached model.

### Step 3: Start the frontend

```bash
cd frontend
python3 -m http.server 3000
```

### Step 4: Open the application

Visit `http://localhost:3000/index.html` in your browser.

---

## 11. Known Limitations

- **Single-request processing**: The server handles one generation request at a time. Concurrent requests will queue.
- **CPU inference speed**: Generation takes roughly 1:1 real-time factor on a modern CPU (a 10-second clip takes ~10 seconds). GPU acceleration is not configured.
- **Local storage only**: Voice samples and outputs are stored on disk. Not suitable for multi-server deployment without shared storage.
- **No persistent user data**: User sessions are stored in `sessionStorage` and lost on browser close.

---

## 12. Future Improvements

- **Background task queue**: Move synthesis to a worker (Celery + Redis) to avoid blocking the HTTP thread.
- **Cloud storage**: Replace local `/voices/` and `/outputs/` with S3 or equivalent.
- **User database**: Store user accounts, generation history, and voice profiles.
- **GPU support**: Add CUDA configuration for significantly faster inference.
- **Rate limiting**: Prevent abuse by limiting requests per user per time window.
