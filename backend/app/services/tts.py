import numpy as np
from pathlib import Path
from typing import Optional

from ..models import get_tts_backend, TTSBackend
from ..config import config


class TTSService:
    """Service for TTS generation"""

    def __init__(self):
        self.backend: Optional[TTSBackend] = None
        self.current_model: Optional[str] = None

    def initialize(self, model_name: Optional[str] = None) -> None:
        """
        Initialize TTS backend with a model

        Args:
            model_name: Name of the model to load. If None, uses the first available model.
        """
        if self.backend is None:
            self.backend = get_tts_backend()

        if model_name is None:
            available_models = self.backend.list_available_models()
            if not available_models:
                raise RuntimeError("No models available for this backend")
            model_name = available_models[0]

        self.backend.load_model(model_name)
        self.current_model = model_name
        print(f"TTS service initialized with model: {model_name}")

    def generate(
        self,
        text: str,
        ref_audio_path: Path,
        ref_text: str,
        progress_callback=None
    ) -> np.ndarray:
        """
        Generate TTS with voice cloning

        Args:
            text: Text to synthesize
            ref_audio_path: Path to reference audio file
            ref_text: Transcription of reference audio
            progress_callback: Optional callback function(current, total, message)
                              for progress updates

        Returns:
            Generated audio as numpy array
        """
        if self.backend is None or not self.backend.is_model_loaded():
            self.initialize()

        if not ref_audio_path.exists():
            raise FileNotFoundError(f"Reference audio not found: {ref_audio_path}")

        print(f"Generating TTS for: {text[:50]}...")

        audio_data = self.backend.generate(
            text=text,
            ref_audio_path=str(ref_audio_path),
            ref_text=ref_text,
            progress_callback=progress_callback
        )

        print("TTS generation complete")
        return audio_data

    def list_available_models(self) -> list[str]:
        """
        List available models for the current backend

        Returns:
            List of model names
        """
        if self.backend is None:
            self.backend = get_tts_backend()

        return self.backend.list_available_models()

    def get_backend_info(self) -> dict:
        """
        Get information about the current backend

        Returns:
            Dictionary with backend information
        """
        if self.backend is None:
            self.backend = get_tts_backend()

        return {
            "platform": self.backend.platform,
            "current_model": self.current_model,
            "available_models": self.backend.list_available_models(),
            "sample_rate": self.backend.sample_rate
        }


# Singleton instance
tts_service = TTSService()
