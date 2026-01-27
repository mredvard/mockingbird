import platform
import os
from pathlib import Path

class Config:
    """Application configuration with platform detection"""

    # Detect platform
    SYSTEM = platform.system()
    MACHINE = platform.machine()

    # Auto-detect backend
    if MACHINE == "arm64" and SYSTEM == "Darwin":
        BACKEND = "mlx"  # Apple Silicon
    else:
        BACKEND = "pytorch"  # Jetson/NVIDIA or other platforms

    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    VOICES_DIR = DATA_DIR / "voices"
    GENERATIONS_DIR = DATA_DIR / "generations"

    # Ensure directories exist
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    GENERATIONS_DIR.mkdir(parents=True, exist_ok=True)

    # Audio settings
    SAMPLE_RATE = 24000
    CHANNELS = 1
    DTYPE = "int16"

    # Model configurations
    MLX_MODELS = [
        "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16",
        "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16",
    ]

    PYTORCH_MODELS = [
        "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    ]

    # Get available models based on backend
    @classmethod
    def get_available_models(cls):
        """Return available models for the current backend"""
        if cls.BACKEND == "mlx":
            return cls.MLX_MODELS
        else:
            return cls.PYTORCH_MODELS

    # API settings
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Transcription settings
    WHISPER_MODEL = "mlx-community/whisper-large-v3-turbo"

    # Recording limits
    MAX_RECORDING_DURATION = 300  # 5 minutes
    MIN_RECORDING_DURATION = 1    # 1 second


config = Config()
