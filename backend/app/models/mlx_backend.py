import numpy as np
from typing import Optional

from mlx_audio.tts import load_model
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
        progress_callback=None,
        **kwargs
    ) -> np.ndarray:
        """
        Generate speech from text with voice cloning using MLX

        Args:
            text: Text to synthesize
            ref_audio_path: Path to reference audio file
            ref_text: Transcription of reference audio
            progress_callback: Optional callback function(current, total, message)
                              called with progress updates during generation
            **kwargs: Additional arguments passed to model.generate()

        Returns:
            Audio data as numpy array (float32, mono)
        """
        import time
        from mlx_audio.tts.generate import load_audio

        if not self._model:
            raise RuntimeError("No model loaded. Call load_model() first.")

        print(f"\n🎵 Starting TTS generation...")
        print(f"📝 Text: {text[:100]}{'...' if len(text) > 100 else ''}")
        print(f"🎙️  Reference: {ref_audio_path}")
        start_time = time.time()

        try:
            # Load reference audio
            if progress_callback:
                progress_callback(1, 5, "Loading reference audio...")

            ref_audio = load_audio(
                ref_audio_path,
                sample_rate=self._model.sample_rate,
                volume_normalize=False
            )

            load_time = time.time() - start_time
            print(f"⏱️  Reference audio loaded in {load_time:.2f}s")

            # Prepare generation parameters
            if progress_callback:
                progress_callback(2, 5, "Preparing generation...")

            gen_kwargs = dict(
                text=text,
                ref_audio=ref_audio,
                ref_text=ref_text,
                verbose=True,  # Show generation stats
                stream=False,
                **kwargs,
            )

            # Generate audio - this returns a generator that yields results
            if progress_callback:
                progress_callback(3, 5, "Generating audio (this may take 1-3 minutes)...")

            gen_start = time.time()
            print(f"🔄 Generating audio tokens...")

            results = list(self._model.generate(**gen_kwargs))

            gen_time = time.time() - gen_start
            print(f"⏱️  Generation completed in {gen_time:.2f}s")

            if not results:
                raise RuntimeError("Model did not generate any audio")

            # Get the first result (for simple cases)
            result = results[0]
            audio_data = np.array(result.audio)

            if progress_callback:
                progress_callback(4, 5, "Processing audio...")

            # Validate audio data
            if audio_data is None or len(audio_data) == 0:
                raise RuntimeError("Generated audio is empty")

            # Ensure mono
            if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]

            # Convert to float32 if needed
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            if progress_callback:
                progress_callback(5, 5, "Complete")

            total_time = time.time() - start_time
            print(f"✅ Total generation time: {total_time:.2f}s")
            print(f"📊 Audio duration: {result.audio_duration}")
            print(f"⚡ Real-time factor: {result.real_time_factor:.2f}x")

            return audio_data

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Generation failed after {elapsed:.2f}s")
            raise RuntimeError(f"TTS generation failed: {str(e)}") from e

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
