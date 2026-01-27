from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional

from ..schemas import Voice, VoiceWithTranscription, TranscriptionUpdate
from ..services import storage_service, transcription_service

router = APIRouter(prefix="/api/voices", tags=["voices"])


@router.post("/", response_model=Voice, status_code=201)
async def create_voice(
    audio: UploadFile = File(..., description="Audio file (WAV format)"),
    name: str = Form(..., description="Voice name"),
    auto_transcribe: bool = Form(True, description="Automatically transcribe audio")
):
    """
    Upload a voice sample

    This endpoint accepts an audio file and creates a new voice profile.
    Optionally transcribes the audio automatically.
    """
    # Validate file type
    if not audio.content_type or "audio" not in audio.content_type.lower():
        raise HTTPException(
            status_code=400,
            detail="File must be an audio file"
        )

    # Read audio data
    audio_data = await audio.read()

    # Transcribe if requested
    transcription = None
    if auto_transcribe:
        try:
            transcription = transcription_service.transcribe_audio_bytes(audio_data)
        except Exception as e:
            print(f"Transcription failed: {e}")
            # Continue without transcription

    # Save voice sample
    voice_metadata = storage_service.create_voice_sample(
        audio_data=audio_data,
        name=name,
        transcription=transcription
    )

    return voice_metadata


@router.get("/", response_model=List[Voice])
async def list_voices():
    """
    Get all voice samples

    Returns a list of all voice profiles, sorted by creation date (newest first).
    """
    voices = storage_service.list_voices()
    return voices


@router.get("/{voice_id}", response_model=VoiceWithTranscription)
async def get_voice(voice_id: str):
    """
    Get voice sample details with transcription

    Returns full voice metadata including transcription text if available.
    """
    voice = storage_service.get_voice(voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")

    # Add transcription if available
    if voice["has_transcription"]:
        transcription = storage_service.get_voice_transcription(voice_id)
        voice["transcription"] = transcription
    else:
        voice["transcription"] = None

    return voice


@router.get("/{voice_id}/audio")
async def get_voice_audio(voice_id: str):
    """
    Download voice audio file

    Returns the original audio file in WAV format.
    """
    audio_path = storage_service.get_voice_audio_path(voice_id)
    if not audio_path:
        raise HTTPException(status_code=404, detail="Voice or audio file not found")

    return FileResponse(
        path=audio_path,
        media_type="audio/wav",
        filename=f"voice_{voice_id}.wav"
    )


@router.get("/{voice_id}/transcription")
async def get_voice_transcription(voice_id: str):
    """
    Get voice transcription text

    Returns just the transcription text if available.
    """
    transcription = storage_service.get_voice_transcription(voice_id)
    if transcription is None:
        raise HTTPException(status_code=404, detail="Transcription not found")

    return {"transcription": transcription}


@router.post("/{voice_id}/transcription", response_model=Voice)
async def update_voice_transcription(
    voice_id: str,
    data: TranscriptionUpdate
):
    """
    Update or add voice transcription

    Manually set the transcription text for a voice sample.
    """
    success = storage_service.update_voice_transcription(
        voice_id=voice_id,
        transcription=data.transcription
    )

    if not success:
        raise HTTPException(status_code=404, detail="Voice not found")

    voice = storage_service.get_voice(voice_id)
    return voice


@router.post("/{voice_id}/transcribe", response_model=Voice)
async def transcribe_voice(voice_id: str):
    """
    Transcribe voice audio

    Manually trigger transcription for a voice sample that wasn't auto-transcribed.
    """
    audio_path = storage_service.get_voice_audio_path(voice_id)
    if not audio_path:
        raise HTTPException(status_code=404, detail="Voice or audio file not found")

    try:
        transcription = transcription_service.transcribe(audio_path)
        storage_service.update_voice_transcription(voice_id, transcription)

        voice = storage_service.get_voice(voice_id)
        return voice
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.delete("/{voice_id}", status_code=204)
async def delete_voice(voice_id: str):
    """
    Delete voice sample

    Permanently deletes the voice profile and all associated files.
    """
    success = storage_service.delete_voice(voice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Voice not found")

    return None
