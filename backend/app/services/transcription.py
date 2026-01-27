import mlx_whisper
from pathlib import Path
from typing import Optional

from ..config import config


class TranscriptionService:
    """Service for speech-to-text transcription"""

    def __init__(self):
        self.model = config.WHISPER_MODEL

    def transcribe(self, audio_path: Path) -> str:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to audio file (WAV format)

        Returns:
            Transcribed text
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"Transcribing {audio_path}...")

        # Transcribe using mlx-whisper
        result = mlx_whisper.transcribe(
            str(audio_path),
            path_or_hf_repo=self.model
        )

        transcription = result["text"].strip()
        print(f"Transcription complete: {transcription[:100]}...")

        return transcription

    def transcribe_audio_bytes(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio from bytes

        Args:
            audio_bytes: Audio file bytes (WAV format)

        Returns:
            Transcribed text
        """
        import tempfile

        # Write to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = Path(tmp_file.name)

        try:
            return self.transcribe(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)


# Singleton instance
transcription_service = TranscriptionService()
