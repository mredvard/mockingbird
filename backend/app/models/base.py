from abc import ABC, abstractmethod
from typing import Optional
import numpy as np


class TTSBackend(ABC):
    """Abstract base class for TTS backends"""

    @abstractmethod
    def load_model(self, model_name: str) -> None:
        """
        Load TTS model

        Args:
            model_name: Name or path of the model to load
        """
        pass

    @abstractmethod
    def generate(
        self,
        text: str,
        ref_audio_path: str,
        ref_text: str,
        **kwargs
    ) -> np.ndarray:
        """
        Generate speech from text with voice cloning

        Args:
            text: Text to convert to speech
            ref_audio_path: Path to reference audio file
            ref_text: Transcription of reference audio
            **kwargs: Additional model-specific parameters

        Returns:
            Audio data as numpy array (shape: [samples,], dtype: float32 or int16)
        """
        pass

    @abstractmethod
    def list_available_models(self) -> list[str]:
        """
        List available models for this backend

        Returns:
            List of model names/paths
        """
        pass

    @property
    @abstractmethod
    def platform(self) -> str:
        """
        Return platform name

        Returns:
            Platform identifier (e.g., 'mlx' or 'pytorch')
        """
        pass

    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """
        Return the sample rate used by the model

        Returns:
            Sample rate in Hz
        """
        pass

    @abstractmethod
    def is_model_loaded(self) -> bool:
        """
        Check if a model is currently loaded

        Returns:
            True if model is loaded, False otherwise
        """
        pass
