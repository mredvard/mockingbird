from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from typing import List, Optional
import uuid

from ..schemas import Generation, GenerationRequest, BackendInfo, TaskStatus as TaskStatusSchema, GenerationTaskResponse
from ..services import storage_service, tts_service, audio_service
from ..services.progress import progress_tracker, TaskStatus

router = APIRouter(prefix="/api/generations", tags=["generations"])


def _generate_speech_background(
    task_id: str,
    text: str,
    voice_id: str,
    model: Optional[str],
    ref_audio_path,
    ref_text: str
):
    """Background task for TTS generation."""
    try:
        # Update progress: Initializing
        progress_tracker.update_progress(
            task_id,
            status=TaskStatus.INITIALIZING,
            progress=10,
            message="Initializing TTS model..."
        )

        # Initialize TTS service
        if model:
            tts_service.initialize(model)
        else:
            tts_service.initialize()

        # Update progress: Generating
        progress_tracker.update_progress(
            task_id,
            status=TaskStatus.GENERATING,
            progress=30,
            message="Generating speech..."
        )

        # Generate TTS
        audio_data = tts_service.generate(
            text=text,
            ref_audio_path=ref_audio_path,
            ref_text=ref_text
        )

        # Validate audio data
        if audio_data is None or len(audio_data) == 0:
            raise ValueError("TTS generation produced no audio data")

        # Update progress: Processing
        progress_tracker.update_progress(
            task_id,
            status=TaskStatus.PROCESSING,
            progress=80,
            message="Processing audio..."
        )

        # Convert to WAV bytes
        audio_bytes = audio_service.audio_to_wav_bytes(audio_data)

        # Validate converted bytes
        if not audio_bytes or len(audio_bytes) < 44:
            raise ValueError("Audio conversion produced invalid WAV data")

        # Calculate duration
        duration = audio_service.get_audio_duration(audio_data)

        # Save generation
        generation_metadata = storage_service.create_generation(
            audio_data=audio_bytes,
            text=text,
            voice_id=voice_id,
            model=tts_service.current_model or "unknown",
            duration=duration
        )

        # Add audio URL
        generation_metadata["audio_url"] = f"/api/generations/{generation_metadata['id']}/audio"

        # Complete task
        progress_tracker.complete_task(task_id, generation_metadata)

    except Exception as e:
        progress_tracker.fail_task(task_id, str(e))


@router.post("/", response_model=Generation, status_code=201)
@router.post("/sync", response_model=Generation, status_code=201)
async def generate_speech(request: GenerationRequest):
    """
    Generate TTS with voice cloning

    Creates a new TTS generation using the specified voice profile and text.
    The model will clone the voice from the reference audio.
    """
    # Get voice sample
    voice = storage_service.get_voice(request.voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")

    # Get voice audio and transcription
    ref_audio_path = storage_service.get_voice_audio_path(request.voice_id)
    if not ref_audio_path:
        raise HTTPException(status_code=404, detail="Voice audio file not found")

    ref_text = storage_service.get_voice_transcription(request.voice_id)
    if not ref_text:
        raise HTTPException(
            status_code=400,
            detail="Voice must have transcription for TTS generation. "
                   "Please transcribe the voice first."
        )

    # Initialize TTS service with specified model
    try:
        if request.model:
            tts_service.initialize(request.model)
        else:
            tts_service.initialize()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize TTS model: {str(e)}"
        )

    # Generate TTS
    try:
        audio_data = tts_service.generate(
            text=request.text,
            ref_audio_path=ref_audio_path,
            ref_text=ref_text
        )

        # Validate audio data
        if audio_data is None or len(audio_data) == 0:
            raise ValueError("TTS generation produced no audio data")

        # Convert to WAV bytes
        audio_bytes = audio_service.audio_to_wav_bytes(audio_data)

        # Validate converted bytes
        if not audio_bytes or len(audio_bytes) < 44:  # WAV header is 44 bytes minimum
            raise ValueError("Audio conversion produced invalid WAV data")

        # Calculate duration
        duration = audio_service.get_audio_duration(audio_data)

        # Save generation
        generation_metadata = storage_service.create_generation(
            audio_data=audio_bytes,
            text=request.text,
            voice_id=request.voice_id,
            model=tts_service.current_model or "unknown",
            duration=duration
        )

        # Add audio URL
        generation_metadata["audio_url"] = f"/api/generations/{generation_metadata['id']}/audio"

        return generation_metadata

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"TTS generation failed: {str(e)}"
        )


@router.get("/", response_model=List[Generation])
async def list_generations(voice_id: Optional[str] = None):
    """
    Get all TTS generations

    Returns a list of all generations, optionally filtered by voice_id.
    Sorted by creation date (newest first).
    """
    generations = storage_service.list_generations(voice_id=voice_id)

    # Add audio URLs
    for gen in generations:
        gen["audio_url"] = f"/api/generations/{gen['id']}/audio"

    return generations


@router.get("/{generation_id}", response_model=Generation)
async def get_generation(generation_id: str):
    """
    Get generation details

    Returns metadata for a specific generation.
    """
    generation = storage_service.get_generation(generation_id)
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")

    # Add audio URL
    generation["audio_url"] = f"/api/generations/{generation_id}/audio"

    return generation


@router.get("/{generation_id}/audio")
async def get_generation_audio(generation_id: str):
    """
    Download generated audio file

    Returns the generated audio in WAV format.
    """
    audio_path = storage_service.get_generation_audio_path(generation_id)
    if not audio_path:
        raise HTTPException(status_code=404, detail="Generation or audio file not found")

    return FileResponse(
        path=audio_path,
        media_type="audio/wav",
        filename=f"generation_{generation_id}.wav"
    )


@router.delete("/{generation_id}", status_code=204)
async def delete_generation(generation_id: str):
    """
    Delete generation

    Permanently deletes the generation and all associated files.
    """
    success = storage_service.delete_generation(generation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Generation not found")

    return None


@router.get("/models/info", response_model=BackendInfo)
async def get_backend_info():
    """
    Get TTS backend information

    Returns information about the current backend platform and available models.
    """
    info = tts_service.get_backend_info()
    return info


@router.get("/models/list", response_model=List[str])
async def list_models():
    """
    List available TTS models

    Returns a list of model names available for the current platform.
    """
    models = tts_service.list_available_models()
    return models


@router.post("/async", response_model=GenerationTaskResponse, status_code=202)
async def generate_speech_async(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate TTS asynchronously with progress tracking

    Starts TTS generation in the background and returns a task ID.
    Use the status endpoint to check progress.
    """
    # Get voice sample
    voice = storage_service.get_voice(request.voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")

    # Get voice audio and transcription
    ref_audio_path = storage_service.get_voice_audio_path(request.voice_id)
    if not ref_audio_path:
        raise HTTPException(status_code=404, detail="Voice audio file not found")

    ref_text = storage_service.get_voice_transcription(request.voice_id)
    if not ref_text:
        raise HTTPException(
            status_code=400,
            detail="Voice must have transcription for TTS generation. "
                   "Please transcribe the voice first."
        )

    # Create task
    task_id = str(uuid.uuid4())
    progress_tracker.create_task(task_id, "Starting TTS generation...")

    # Start background generation
    background_tasks.add_task(
        _generate_speech_background,
        task_id=task_id,
        text=request.text,
        voice_id=request.voice_id,
        model=request.model,
        ref_audio_path=ref_audio_path,
        ref_text=ref_text
    )

    return {
        "task_id": task_id,
        "message": "Generation started",
        "status_url": f"/api/generations/tasks/{task_id}"
    }


@router.get("/tasks/{task_id}", response_model=TaskStatusSchema)
async def get_task_status(task_id: str):
    """
    Get generation task status and progress

    Returns the current status, progress percentage, and result (if completed).
    """
    task = progress_tracker.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: str):
    """
    Delete a task from tracking

    Removes the task and its progress information.
    Note: This does not cancel a running task, only removes it from tracking.
    """
    task = progress_tracker.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    progress_tracker.delete_task(task_id)
    return None
