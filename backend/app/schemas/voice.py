from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VoiceBase(BaseModel):
    """Base voice schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Voice name")


class VoiceCreate(VoiceBase):
    """Schema for creating a voice"""
    pass


class Voice(VoiceBase):
    """Schema for voice response"""
    id: str = Field(..., description="Voice UUID")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    has_transcription: bool = Field(..., description="Whether transcription is available")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")

    class Config:
        from_attributes = True


class VoiceWithTranscription(Voice):
    """Schema for voice with transcription text"""
    transcription: Optional[str] = Field(None, description="Transcription text")


class TranscriptionUpdate(BaseModel):
    """Schema for updating voice transcription"""
    transcription: str = Field(..., min_length=1, description="Transcription text")
