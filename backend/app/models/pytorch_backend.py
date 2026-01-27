import numpy as np
from typing import Optional

from .base import TTSBackend
from ..config import config


class PyTorchBackend(TTSBackend):
    """PyTorch-based TTS backend for NVIDIA GPUs (Jetson)"""

    def __init__(self):
        self._current_model: Optional[str] = None
        self._sample_rate = config.SAMPLE_RATE
        self._model = None
        self._tokenizer = None

    def load_model(self, model_name: str) -> None:
        """
        Load TTS model

        TODO: Implement PyTorch Qwen3-TTS integration
        This will be implemented when testing on Jetson
        """
        if model_name not in self.list_available_models():
            raise ValueError(f"Model {model_name} not available for PyTorch backend")

        raise NotImplementedError(
            "PyTorch backend not yet implemented. "
            "This backend is for NVIDIA GPU platforms like Jetson Orin Nano. "
            "On Mac, use the MLX backend instead."
        )

    def generate(
        self,
        text: str,
        ref_audio_path: str,
        ref_text: str,
        **kwargs
    ) -> np.ndarray:
        """
        Generate speech from text with voice cloning using PyTorch

        TODO: Implement using transformers library
        """
        raise NotImplementedError("PyTorch backend not yet implemented")

    def list_available_models(self) -> list[str]:
        """List available PyTorch models"""
        return config.PYTORCH_MODELS

    @property
    def platform(self) -> str:
        """Return platform name"""
        return "pytorch"

    @property
    def sample_rate(self) -> int:
        """Return the sample rate"""
        return self._sample_rate

    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded"""
        return self._model is not None
