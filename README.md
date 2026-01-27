# TTS Voice Cloning Web Application

Text-to-speech web application with voice cloning capabilities, supporting both Apple Silicon (MLX) and NVIDIA GPUs (PyTorch).

## Features

- Web-based interface for voice recording and TTS generation
- Voice cloning with reference audio samples
- Automatic speech-to-text transcription
- RESTful API backend
- Multi-platform support (MLX for Mac, PyTorch for Jetson)
- Voice library management
- Generation history

## Architecture

The application consists of:

- **Backend**: FastAPI-based REST API with dual backend support (MLX/PyTorch)
- **Frontend**: React + TypeScript + Vite with Tailwind CSS
- **TTS Models**: Qwen3-TTS (0.6B and 1.7B variants)
- **STT Model**: Whisper Large v3 Turbo

## Prerequisites

### For Mac (Apple Silicon)
- Python 3.12+
- Node.js 20+ and npm
- [uv](https://github.com/astral-sh/uv) package manager

### For Jetson Orin Nano
- Python 3.12+
- Node.js 20+ and npm
- CUDA-compatible PyTorch

## Installation

### 1. Backend Setup

#### On Mac (Apple Silicon)
```bash
# Install dependencies with MLX backend
uv sync --extra mlx
```

#### On Jetson (NVIDIA GPU)
```bash
# Install dependencies with PyTorch backend
uv sync --extra pytorch
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

## Usage

### Starting the Application

#### 1. Start the Backend API

```bash
# From project root
uv run python -m backend.app.main
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- OpenAPI Schema: `http://localhost:8000/redoc`

#### 2. Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The web interface will be available at `http://localhost:5173`

### Web Interface Workflow

1. **Record Voice Sample**
   - Navigate to the web interface
   - Click "Record Voice" and speak for a few seconds
   - The audio will be automatically transcribed
   - Save the voice profile

2. **Generate TTS with Voice Cloning**
   - Select a voice profile from your library
   - Enter the text you want to synthesize
   - Choose a TTS model (if desired)
   - Generate and listen to the result

3. **Manage Voice Library**
   - View all saved voice profiles
   - Play back reference audio
   - Edit transcriptions manually
   - Delete unwanted profiles

4. **View Generation History**
   - Browse all previously generated audio
   - Replay or download generations
   - Filter by voice profile

### CLI Usage (Original Functionality)

The original CLI tools are still available:

#### Record voice sample
```bash
# Record for 5 seconds (default)
uv run python record.py

# Record for 10 seconds
uv run python record.py 10
```

#### Transcribe audio
```bash
# Transcribe voice_sample.wav (default)
uv run python transcribe.py

# Transcribe a specific file
uv run python transcribe.py my_recording.wav
```

#### Generate TTS directly
```bash
uv run python -m mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16 \
  --text "Hello, this is a test." \
  --play
```

#### Voice cloning via CLI
```bash
uv run python -m mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16 \
  --text "Whatever you want it to say." \
  --ref_audio voice_sample.wav \
  --ref_text "What you said in the recording." \
  --play
```

## API Endpoints

### Voices
- `POST /api/voices` - Upload voice sample with optional auto-transcription
- `GET /api/voices` - List all voice samples
- `GET /api/voices/{id}` - Get voice details with transcription
- `GET /api/voices/{id}/audio` - Download voice audio
- `POST /api/voices/{id}/transcribe` - Transcribe voice sample
- `DELETE /api/voices/{id}` - Delete voice sample

### Generations
- `POST /api/generations` - Generate TTS with voice cloning
- `GET /api/generations` - List all generations
- `GET /api/generations/{id}` - Get generation details
- `GET /api/generations/{id}/audio` - Download generated audio
- `DELETE /api/generations/{id}` - Delete generation

### Models
- `GET /api/generations/models/info` - Get backend information
- `GET /api/generations/models/list` - List available models

### Health
- `GET /api/health` - Health check

## Available Models

### MLX Backend (Mac)
- `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16`
- `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16`

### PyTorch Backend (Jetson)
- `Qwen/Qwen3-TTS-12Hz-0.6B-Base`
- `Qwen/Qwen3-TTS-12Hz-1.7B-Base`

Note: PyTorch backend implementation is pending. Currently only MLX backend is fully functional.

## Project Structure

```
TTS/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration & platform detection
│   │   ├── models/              # TTS backend implementations
│   │   ├── services/            # Business logic services
│   │   ├── routes/              # API endpoints
│   │   └── schemas/             # Pydantic models
│   └── data/                    # File storage
│       ├── voices/              # Voice samples
│       └── generations/         # Generated audio
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API client
│   │   └── types/               # TypeScript types
│   └── ...                      # Vite config files
├── record.py                    # CLI recording tool
├── transcribe.py                # CLI transcription tool
├── pyproject.toml               # Python dependencies
└── README.md
```

## Configuration

### Backend Configuration
The backend auto-detects the platform and selects the appropriate backend:
- Apple Silicon (arm64 + Darwin) → MLX backend
- Other platforms → PyTorch backend

Configuration can be found in [backend/app/config.py](backend/app/config.py).

### Frontend Configuration
Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
```

## Data Storage

All data is stored in the `backend/data/` directory:

```
backend/data/
├── voices/{voice_id}/
│   ├── audio.wav
│   ├── transcription.txt
│   └── metadata.json
└── generations/{generation_id}/
    ├── audio.wav
    └── metadata.json
```

## Development

### Backend Development
```bash
# Run with auto-reload
uv run uvicorn backend.app.main:app --reload

# Run tests (when implemented)
uv run pytest
```

### Frontend Development
```bash
cd frontend

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Troubleshooting

### Backend Issues

**Import errors**: Ensure all dependencies are installed with `uv sync --extra mlx`

**Model download failures**: First generation will download models (~1.5-3.5GB). Ensure good internet connection.

**Audio device errors**: Check that your microphone is accessible and not being used by another application.

### Frontend Issues

**API connection errors**: Verify the backend is running on `http://localhost:8000`

**Build errors**: Ensure Node.js version is 20+ with `node --version`

**CORS errors**: Check that CORS origins are configured correctly in [backend/app/config.py](backend/app/config.py)

## Current Status

### ✅ Completed
- Backend API with FastAPI
- Dual-backend architecture (MLX/PyTorch abstraction)
- MLX backend implementation
- Voice management endpoints (upload, list, get, delete, transcribe)
- TTS generation endpoints
- Storage service for voice samples and generations
- Audio recording and transcription services
- Frontend project setup with Vite + React + TypeScript + Tailwind CSS
- TypeScript types for API integration
- API service layer

### 🚧 In Progress / TODO
- Frontend UI components (buttons, cards, inputs, audio player)
- Voice recording interface component
- Voice library browser component
- TTS generation interface component
- React Query hooks for data fetching
- Main application routing and layout
- PyTorch backend implementation (for Jetson)

## Contributing

Contributions are welcome! Please ensure:
- Backend code follows FastAPI best practices
- Frontend code uses TypeScript with proper typing
- All new features include appropriate error handling
- API endpoints are documented in docstrings

## License

[Add license information]

## Acknowledgments

- [MLX Audio](https://github.com/ml-explore/mlx-audio) - MLX-based audio models
- [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) - TTS model
- [MLX Whisper](https://github.com/ml-explore/mlx-whisper) - Speech recognition
