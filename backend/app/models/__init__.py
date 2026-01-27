from .base import TTSBackend
from .mlx_backend import MLXBackend
from .pytorch_backend import PyTorchBackend
from ..config import config


def get_tts_backend() -> TTSBackend:
    """
    Factory function to get the appropriate TTS backend based on platform

    Returns:
        TTSBackend instance (MLX or PyTorch)
    """
    if config.BACKEND == "mlx":
        return MLXBackend()
    elif config.BACKEND == "pytorch":
        return PyTorchBackend()
    else:
        raise ValueError(f"Unknown backend: {config.BACKEND}")


__all__ = ["TTSBackend", "MLXBackend", "PyTorchBackend", "get_tts_backend"]
