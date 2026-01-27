# Claude Code Session Notes

## Project Overview
TTS Voice Cloning Web Application with MLX (Apple Silicon) and PyTorch (NVIDIA GPU) backend support.

## Recent Work Completed

### 1. MLX Backend Refactored to Use Python API + Progress Tracking (2026-01-27)
**Migration from subprocess to direct Python imports with detailed timing and progress tracking**

**Problem**: The MLX backend was calling `python -m mlx_audio.tts.generate` via subprocess, which had several limitations:
- High overhead from spawning processes
- Poor error handling (parsing stderr)
- **No visibility into generation progress** (appeared "frozen" for 40+ seconds)
- Model loaded/unloaded on every generation
- Difficult to debug

**Solution**: Refactored to use `mlx_audio` Python API directly with progress callbacks and detailed timing:

```python
from mlx_audio.tts import load_model
import mlx.core as mx

# Load model once, reuse for multiple generations
model = load_model(model_path=model_name)

# Call model.generate() directly with progress callback
results = list(model.generate(text=text, ref_audio=ref_audio, ref_text=ref_text, ...))
```

**Key Improvements**:
1. **Model Persistence**: Model stays loaded in memory between generations
2. **Progress Tracking**: Progress callback support for real-time updates during generation
3. **Detailed Timing**: Logs timing for each stage with emoji indicators
4. **Direct Error Handling**: Python exceptions with full stack traces
5. **Better Resource Management**: Added `unload_model()` method with `mx.clear_cache()`
6. **Observability**: Clear visibility into what's happening during the 40+ second generation

**Performance Metrics** (measured on Apple Silicon):
- **Reference audio loading**: ~0.04s
- **Audio generation**: ~40s (bottleneck - this is the MLX model inference time)
- **Audio processing**: ~0.04s
- **Total**: ~45s for 3.6s of audio
- **Real-time factor**: 0.09x (11 seconds to generate 1 second of audio)

**Changes Made**:

1. **`backend/app/models/mlx_backend.py`**:
   - Removed subprocess/tempfile/generate_audio wrapper
   - Added `_model` instance variable to persist loaded model
   - Replaced subprocess with direct `model.generate()` call
   - Added `progress_callback` parameter for real-time progress updates
   - Added detailed timing logs: 🎵 🔄 ⏱️ ✅ ❌ 📊 ⚡
   - Added `unload_model()` for memory cleanup

2. **`backend/app/services/tts.py`**:
   - Added `progress_callback` parameter to pass through to backend

3. **`backend/app/routes/generation.py`**:
   - Added timing logs to background generation task
   - Implemented `generation_progress()` callback to update ProgressTracker
   - Added breakdown of initialization, generation, and processing times

**Testing**:
- ✅ Synchronous generation: 41-47s for short Spanish text
- ✅ Async with progress: Can observe intermediate states (10% → 54% → 100%)
- ✅ Server logs show detailed timing breakdown
- ✅ Progress tracking now captures real generation stages

### 2. Backend Testing Infrastructure (2026-01-27)
Created comprehensive test suite for the FastAPI backend:

- **Test Files Created**:
  - `tests/conftest.py` - Test fixtures and configuration
  - `tests/test_voice_endpoints.py` - 16 tests for voice CRUD operations
  - `tests/test_generation_endpoints.py` - 16 tests for generation validation
  - `tests/test_models_health_endpoints.py` - 17 tests for models, health, API docs
  - `tests/test_generation_integration.py` - 4 integration tests for actual TTS generation
  - `pytest.ini` - Pytest configuration with markers

- **Test Coverage**: 41 passing unit tests, 4 integration tests (marked separately)
- **Key Features**:
  - Test isolation using temporary directories
  - Fixtures for voice samples and transcriptions
  - Spanish voice sample in `tests/fixtures/voice_sample.wav`
  - Integration tests marked with `@pytest.mark.integration`

### 2. Progress Tracking for TTS Generation
Implemented async generation with real-time progress tracking:

- **New Files**:
  - `backend/app/services/progress.py` - ProgressTracker service
  - `backend/app/schemas/task.py` - TaskStatus and GenerationTaskResponse schemas

- **New Endpoints**:
  - `POST /api/generations/async` - Start async generation (returns task_id)
  - `GET /api/generations/tasks/{task_id}` - Check progress (0-100%)
  - `DELETE /api/generations/tasks/{task_id}` - Remove task from tracking

- **Progress States**:
  - `pending` (0%) - Task queued
  - `initializing` (10%) - Loading model
  - `generating` (30-70%) - Creating speech
  - `processing` (80-90%) - Post-processing
  - `completed` (100%) - Done
  - `failed` - Error occurred

### 3. Manual Testing Scripts
Created scripts for manual testing and debugging:

- `test_generation_manual.py` - Manual test script that saves files to `backend/data/generations/`
  - Supports both sync and async generation
  - Run: `uv run python test_generation_manual.py` (sync) or `uv run python test_generation_manual.py async`
- `test_tts_direct.py` - Direct TTS test bypassing API layer for debugging

### 4. MLX Backend Bug Fix (CRITICAL)
**Issue**: TTS generation was producing empty audio data with error: `File format b'' not understood`

**Root Cause**: The `mlx_audio` CLI expects:
- `--output` parameter to be a **directory** (not a file path)
- Saves files as `audio_000.wav`, `audio_001.wav`, etc. inside that directory

**Fix Applied** in `backend/app/models/mlx_backend.py`:
```python
# Create temporary directory (not file)
temp_dir = tempfile.mkdtemp(prefix="tts_")
output_dir = Path(temp_dir)

# Pass directory to mlx_audio CLI
cmd = ["python", "-m", "mlx_audio.tts.generate", "--output", str(output_dir), ...]

# Find generated audio files (audio_000.wav, audio_001.wav, etc.)
audio_files = list(output_dir.glob("audio_*.wav"))
output_path = audio_files[0]
```

### 5. Model Configuration Update
Set `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16` as the default model:

- Updated `backend/app/config.py` - Reordered MLX_MODELS list (first = default)
- Updated all integration tests to explicitly use 1.7B model
- Updated `README.md` to reflect 1.7B as default

## Current Status

### Working Features
- ✅ TTS generation (sync and async)
- ✅ Progress tracking for async generation
- ✅ Voice cloning with reference audio
- ✅ Comprehensive test suite (49 tests total)
- ✅ Manual testing scripts
- ✅ MLX backend fully functional

### Known Issues
1. **Test Isolation**: One test failure due to seeing manual test data in real data directory (non-critical)
2. **Progress Tracking Test**: Generation too fast to observe intermediate stages (non-critical)

## Running the Project

### Backend API
```bash
# Start the FastAPI server
uv run python -m backend.app.main
```

API available at: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Tests
```bash
# Unit tests (~3 seconds)
uv run pytest

# Integration tests (~5-15 minutes, requires model download on first run)
uv run pytest -m integration

# Specific test file
uv run pytest tests/test_voice_endpoints.py -v
```

### Manual Generation Testing
```bash
# Synchronous generation (creates files in backend/data/generations/)
uv run python test_generation_manual.py

# Asynchronous generation with progress tracking
uv run python test_generation_manual.py async

# Direct TTS test (bypasses API for debugging)
uv run python test_tts_direct.py
```

## Important Files

### Core Backend
- `backend/app/models/mlx_backend.py` - MLX TTS backend (FIXED: output path handling)
- `backend/app/services/tts.py` - TTS service wrapper
- `backend/app/services/progress.py` - Progress tracking for async generation
- `backend/app/routes/generation.py` - Generation API endpoints
- `backend/app/config.py` - Configuration (1.7B model as default)

### Testing
- `tests/conftest.py` - Test fixtures
- `tests/fixtures/voice_sample.wav` - Spanish voice sample for testing
- `test_generation_manual.py` - Manual testing script
- `test_tts_direct.py` - Direct TTS debugging script

### Documentation
- `README.md` - Main project documentation
- `CLAUDE.md` - This file (session notes)

## Model Information

### MLX Backend (Mac with Apple Silicon)
- **Default**: `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16` (~3.5GB)
- **Alternative**: `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` (~1.5GB)

### PyTorch Backend (Jetson/NVIDIA)
- **Default**: `Qwen/Qwen3-TTS-12Hz-1.7B-Base`
- **Alternative**: `Qwen/Qwen3-TTS-12Hz-0.6B-Base`
- **Status**: PyTorch backend implementation pending

### Transcription Model
- `mlx-community/whisper-large-v3-turbo` (for voice transcription)

## Architecture Notes

### TTS Generation Flow
1. User provides text + selects voice profile
2. API retrieves voice audio sample + transcription
3. TTS service initializes model (if not loaded)
4. MLX backend calls `python -m mlx_audio.tts.generate` via subprocess
5. Subprocess saves audio to temporary directory as `audio_000.wav`
6. Backend reads generated audio, converts to float32, returns numpy array
7. Audio service converts to WAV bytes
8. Storage service saves to `backend/data/generations/{id}/audio.wav`

### Progress Tracking Flow (Async)
1. User POST to `/api/generations/async` - receives task_id
2. Background task updates progress via ProgressTracker
3. User polls `/api/generations/tasks/{task_id}` for status
4. States: pending → initializing → generating → processing → completed

## Dependencies

### Python (Backend)
- `fastapi` - REST API framework
- `uvicorn` - ASGI server
- `mlx-audio` - MLX TTS models (Apple Silicon)
- `mlx-whisper` - MLX transcription (Apple Silicon)
- `scipy` - Audio processing
- `sounddevice` - Audio recording
- `pytest` - Testing framework
- `httpx` - Test client for FastAPI
- `requests` - Manual testing scripts

### Node.js (Frontend)
- React + TypeScript + Vite
- Tailwind CSS

## Next Steps / TODO

- [ ] Fix test isolation issue (tests seeing manual test data). Test data should go to a different folder and not interfere with manual or real data.
- [ ] Improve progress tracking tests to better observe intermediate states
- [ ] Implement PyTorch backend for Jetson/NVIDIA platforms
- [ ] Add generation queue management
- [ ] Add voice profile management UI improvements
- [ ] Add audio playback controls in frontend
- [ ] Add export/import for voice profiles
- [ ] Add model selection in frontend UI

## Debugging Tips

### TTS Generation Not Working?
1. Run `test_tts_direct.py` to isolate the issue (API vs TTS backend)
2. Check that model is downloaded: `~/.cache/huggingface/hub/models--mlx-community--Qwen3-TTS-12Hz-1.7B-Base-bf16`
3. Check voice sample exists and has transcription
4. Check subprocess output in backend logs

### Tests Failing?
1. Check test isolation: temporary directories should be cleaned up
2. Check that `tests/fixtures/voice_sample.wav` exists
3. Integration tests require model download on first run (slow)
4. Run with `-v` for verbose output: `uv run pytest -v`

### Audio Quality Issues?
- Check sample rate (should be 24000 Hz)
- Check audio format (mono, int16 or float32)
- Check reference audio quality
- Ensure transcription matches reference audio accurately

---

**Last Updated**: 2026-01-27
**Claude Session**: Fixed MLX backend output path handling, implemented progress tracking, created comprehensive test suite
