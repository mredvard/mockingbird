import numpy as np
from pathlib import Path
from typing import Optional
import subprocess
import tempfile
import wave
from scipy.io import wavfile

from .base import TTSBackend
from ..config import config


class MLXBackend(TTSBackend):
    """MLX-based TTS backend for Apple Silicon"""

    def __init__(self):
        self._current_model: Optional[str] = None
        self._sample_rate = config.SAMPLE_RATE

    def load_model(self, model_name: str) -> None:
        """
        Load TTS model

        Note: MLX models are loaded on-demand during generation
        We just store the model name here
        """
        if model_name not in self.list_available_models():
            raise ValueError(f"Model {model_name} not available for MLX backend")

        self._current_model = model_name
        print(f"MLX backend configured to use model: {model_name}")

    def generate(
        self,
        text: str,
        ref_audio_path: str,
        ref_text: str,
        **kwargs
    ) -> np.ndarray:
        """
        Generate speech from text with voice cloning using MLX

        This uses the mlx_audio CLI under the hood
        """
        if not self._current_model:
            raise RuntimeError("No model loaded. Call load_model() first.")

        # Create temporary file for output
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            output_path = tmp_file.name

        try:
            # Build command
            cmd = [
                "python", "-m", "mlx_audio.tts.generate",
                "--model", self._current_model,
                "--text", text,
                "--ref_audio", ref_audio_path,
                "--ref_text", ref_text,
                "--output", output_path,
            ]

            # Run generation
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Read the generated audio
            sample_rate, audio_data = wavfile.read(output_path)

            # Ensure mono
            if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]

            # Convert to float32 if needed
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0

            return audio_data

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"TTS generation failed: {e.stderr}")
        finally:
            # Clean up temporary file
            Path(output_path).unlink(missing_ok=True)

    def list_available_models(self) -> list[str]:
        """List available MLX models"""
        return config.MLX_MODELS

    @property
    def platform(self) -> str:
        """Return platform name"""
        return "mlx"

    @property
    def sample_rate(self) -> int:
        """Return the sample rate"""
        return self._sample_rate

    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded"""
        return self._current_model is not None
