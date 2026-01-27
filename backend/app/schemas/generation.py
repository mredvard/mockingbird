from pydantic import BaseModel, Field
from typing import Optional


class GenerationRequest(BaseModel):
    """Schema for TTS generation request"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    voice_id: str = Field(..., description="Reference voice UUID")
    model: Optional[str] = Field(None, description="Model name (uses default if not specified)")


class Generation(BaseModel):
    """Schema for generation response"""
    id: str = Field(..., description="Generation UUID")
    text: str = Field(..., description="Generated text")
    voice_id: str = Field(..., description="Reference voice UUID")
    model: str = Field(..., description="Model used")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    audio_url: str = Field(..., description="URL to download audio")

    class Config:
        from_attributes = True


class BackendInfo(BaseModel):
    """Schema for backend information"""
    platform: str = Field(..., description="Backend platform (mlx or pytorch)")
    current_model: Optional[str] = Field(None, description="Currently loaded model")
    available_models: list[str] = Field(..., description="List of available models")
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
