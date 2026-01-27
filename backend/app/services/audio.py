import sounddevice as sd
import scipy.io.wavfile as wavfile
import numpy as np
from pathlib import Path
import io

from ..config import config


class AudioService:
    """Service for audio recording and processing"""

    def __init__(self):
        self.sample_rate = config.SAMPLE_RATE
        self.channels = config.CHANNELS

    def record_audio(self, duration: float) -> np.ndarray:
        """
        Record audio from microphone

        Args:
            duration: Recording duration in seconds

        Returns:
            Audio data as numpy array
        """
        if duration < config.MIN_RECORDING_DURATION:
            raise ValueError(f"Duration must be at least {config.MIN_RECORDING_DURATION} seconds")

        if duration > config.MAX_RECORDING_DURATION:
            raise ValueError(f"Duration must not exceed {config.MAX_RECORDING_DURATION} seconds")

        print(f"Recording for {duration} seconds...")

        # Record audio
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16'
        )
        sd.wait()

        print("Recording complete")
        return recording.flatten()

    def save_audio(self, audio_data: np.ndarray, file_path: Path) -> None:
        """
        Save audio data to WAV file

        Args:
            audio_data: Audio data as numpy array
            file_path: Path to save the WAV file
        """
        wavfile.write(file_path, self.sample_rate, audio_data)

    def load_audio(self, file_path: Path) -> tuple[int, np.ndarray]:
        """
        Load audio from WAV file

        Args:
            file_path: Path to WAV file

        Returns:
            Tuple of (sample_rate, audio_data)
        """
        return wavfile.read(file_path)

    def audio_to_wav_bytes(self, audio_data: np.ndarray) -> bytes:
        """
        Convert audio numpy array to WAV file bytes

        Args:
            audio_data: Audio data as numpy array

        Returns:
            WAV file as bytes
        """
        # Ensure int16 dtype
        if audio_data.dtype == np.float32:
            audio_data = (audio_data * 32767).astype(np.int16)
        elif audio_data.dtype != np.int16:
            audio_data = audio_data.astype(np.int16)

        # Write to bytes buffer
        buffer = io.BytesIO()
        wavfile.write(buffer, self.sample_rate, audio_data)
        buffer.seek(0)
        return buffer.read()

    def wav_bytes_to_audio(self, wav_bytes: bytes) -> tuple[int, np.ndarray]:
        """
        Convert WAV file bytes to audio numpy array

        Args:
            wav_bytes: WAV file as bytes

        Returns:
            Tuple of (sample_rate, audio_data)
        """
        buffer = io.BytesIO(wav_bytes)
        return wavfile.read(buffer)

    def get_audio_duration(self, audio_data: np.ndarray) -> float:
        """
        Calculate audio duration in seconds

        Args:
            audio_data: Audio data as numpy array

        Returns:
            Duration in seconds
        """
        return len(audio_data) / self.sample_rate


# Singleton instance
audio_service = AudioService()
