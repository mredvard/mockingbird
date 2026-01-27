import numpy as np
from pathlib import Path
from typing import Optional
import tempfile

from mlx_audio.tts import load_model
from mlx_audio.tts.generate import generate_audio
import mlx.core as mx

from .base import TTSBackend
from ..config import config


class MLXBackend(TTSBackend):
    """MLX-based TTS backend for Apple Silicon"""

    def __init__(self):
        self._current_model_name: Optional[str] = None
        self._model = None  # Store loaded model instance
        self._sample_rate = config.SAMPLE_RATE

    def load_model(self, model_name: str) -> None:
        """
        Load TTS model into memory

        Unlike the subprocess approach, we now keep the model loaded
        for better performance on subsequent generations
        """
        if model_name not in self.list_available_models():
            raise ValueError(f"Model {model_name} not available for MLX backend")

        # Only reload if it's a different model
        if self._current_model_name != model_name:
            print(f"Loading MLX model: {model_name}")
            self._model = load_model(model_path=model_name)
            self._current_model_name = model_name
            print(f"MLX model loaded successfully: {model_name}")
        else:
            print(f"MLX model already loaded: {model_name}")

    def generate(
        self,
        text: str,
        ref_audio_path: str,
        ref_text: str,
        **kwargs
    ) -> np.ndarray:
        """
        Generate speech from text with voice cloning using MLX

        Now uses the Python API directly instead of subprocess
        """
        if not self._model:
            raise RuntimeError("No model loaded. Call load_model() first.")

        # Create temporary directory for output
        temp_dir = tempfile.mkdtemp(prefix="tts_")
        output_dir = Path(temp_dir)

        try:
            # Generate audio using Python API directly
            # This replaces the subprocess call with a direct function call
            generate_audio(
                text=text,
                model=self._model,  # Pass loaded model instance
                ref_audio=ref_audio_path,
                ref_text=ref_text,
                output_path=str(output_dir),
                file_prefix="audio",
                audio_format="wav",
                play=False,
                verbose=False,  # Set to True for debugging
                join_audio=False,
            )

            # Find the generated audio file (saves as audio_000.wav, audio_001.wav, etc.)
            audio_files = list(output_dir.glob("audio_*.wav"))
            if not audio_files:
                raise RuntimeError(f"TTS generation did not create any audio files in: {output_dir}")

            # Use the first audio file
            output_path = audio_files[0]

            if output_path.stat().st_size == 0:
                raise RuntimeError(f"TTS generation created empty output file: {output_path}")

            # Read the generated audio using scipy
            from scipy.io import wavfile
            sample_rate, audio_data = wavfile.read(str(output_path))

            # Validate audio data
            if audio_data is None or len(audio_data) == 0:
                raise RuntimeError(f"TTS generation produced empty audio data")

            # Ensure mono
            if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]

            # Convert to float32 if needed
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0

            return audio_data

        except Exception as e:
            # Now we get proper Python exceptions instead of parsing subprocess output
            raise RuntimeError(f"TTS generation failed: {str(e)}") from e
        finally:
            # Clean up temporary directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

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
        return self._model is not None

    def unload_model(self) -> None:
        """Unload the current model to free memory"""
        if self._model:
            print(f"Unloading MLX model: {self._current_model_name}")
            del self._model
            self._model = None
            self._current_model_name = None
            # Clear MLX cache
            mx.clear_cache()
            print("MLX model unloaded and cache cleared")
