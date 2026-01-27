"""Audio format conversion utilities"""

import io
from pathlib import Path
from typing import Union
import numpy as np
from scipy.io import wavfile


def convert_to_wav(audio_data: bytes, target_sample_rate: int = 24000) -> bytes:
    """
    Convert audio data to WAV format

    Handles various input formats (WebM, MP3, etc.) using ffmpeg for broad format support.

    Args:
        audio_data: Raw audio file bytes (any format)
        target_sample_rate: Target sample rate for output WAV

    Returns:
        WAV format audio bytes
    """
    # First, check if it's already a valid WAV file
    if _is_valid_wav(audio_data):
        print("Audio is already in WAV format")
        return audio_data

    # Use ffmpeg for conversion (supports WebM, MP3, etc.)
    try:
        return _convert_with_ffmpeg(audio_data, target_sample_rate)
    except Exception as e:
        # Try soundfile as fallback (supports fewer formats but no external deps)
        try:
            import soundfile as sf

            # Read audio data using soundfile
            audio_array, sample_rate = sf.read(io.BytesIO(audio_data))

            # Resample if needed
            if sample_rate != target_sample_rate:
                from scipy.signal import resample
                num_samples = int(len(audio_array) * target_sample_rate / sample_rate)
                audio_array = resample(audio_array, num_samples)
                sample_rate = target_sample_rate

            # Ensure mono
            if len(audio_array.shape) > 1:
                audio_array = audio_array[:, 0]

            # Convert to int16 for WAV
            if audio_array.dtype != np.int16:
                if np.issubdtype(audio_array.dtype, np.floating):
                    audio_array = np.clip(audio_array, -1.0, 1.0)
                    audio_array = (audio_array * 32767).astype(np.int16)
                else:
                    audio_array = audio_array.astype(np.int16)

            # Write to WAV bytes
            wav_buffer = io.BytesIO()
            wavfile.write(wav_buffer, sample_rate, audio_array)
            wav_buffer.seek(0)

            return wav_buffer.read()

        except Exception as e2:
            raise RuntimeError(f"Audio conversion failed: {str(e)}. Fallback also failed: {str(e2)}")


def _is_valid_wav(audio_data: bytes) -> bool:
    """Check if audio data is already a valid WAV file"""
    # WAV files start with "RIFF" and have "WAVE" at offset 8
    if len(audio_data) < 12:
        return False
    return audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE'


def _convert_with_ffmpeg(audio_data: bytes, target_sample_rate: int) -> bytes:
    """
    Fallback conversion using ffmpeg subprocess

    Args:
        audio_data: Raw audio file bytes
        target_sample_rate: Target sample rate

    Returns:
        WAV format audio bytes
    """
    import subprocess
    import tempfile

    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as input_file:
        input_file.write(audio_data)
        input_path = input_file.name

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_file:
        output_path = output_file.name

    try:
        # Convert using ffmpeg
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ar", str(target_sample_rate),  # Sample rate
            "-ac", "1",  # Mono
            "-f", "wav",  # Output format
            "-y",  # Overwrite
            output_path
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        # Read converted WAV
        with open(output_path, "rb") as f:
            return f.read()

    finally:
        # Cleanup
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def get_audio_duration(audio_data: bytes) -> float:
    """
    Get duration of audio data in seconds

    Args:
        audio_data: Audio file bytes (any format)

    Returns:
        Duration in seconds
    """
    try:
        import soundfile as sf
        audio_array, sample_rate = sf.read(io.BytesIO(audio_data))
        return len(audio_array) / sample_rate
    except:
        # Fallback: try to parse as WAV
        try:
            sample_rate, audio_array = wavfile.read(io.BytesIO(audio_data))
            return len(audio_array) / sample_rate
        except:
            return None
