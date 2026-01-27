from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional

from ..schemas import Generation, GenerationRequest, BackendInfo
from ..services import storage_service, tts_service, audio_service

router = APIRouter(prefix="/api/generations", tags=["generations"])


@router.post("/", response_model=Generation, status_code=201)
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

        # Convert to WAV bytes
        audio_bytes = audio_service.audio_to_wav_bytes(audio_data)

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
