from pathlib import Path
from datetime import datetime
import json
import uuid
from typing import Optional, Dict, Any, List
import shutil

from ..config import config
from ..utils.audio import convert_to_wav, get_audio_duration


class StorageService:
    """Manages filesystem storage for voices and generations"""

    def __init__(self):
        self.voices_dir = config.VOICES_DIR
        self.generations_dir = config.GENERATIONS_DIR

    def create_voice_sample(
        self,
        audio_data: bytes,
        name: str,
        transcription: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new voice sample with metadata

        Args:
            audio_data: Raw audio file bytes (any format - will be converted to WAV)
            name: Human-readable name for the voice
            transcription: Optional transcription text

        Returns:
            Voice metadata dictionary
        """
        voice_id = str(uuid.uuid4())
        voice_dir = self.voices_dir / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)

        # Convert audio to WAV format (handles WebM, MP3, etc.)
        print(f"Converting audio to WAV format (sample rate: {config.SAMPLE_RATE})")
        try:
            wav_data = convert_to_wav(audio_data, target_sample_rate=config.SAMPLE_RATE)
        except Exception as e:
            print(f"Audio conversion failed: {e}")
            # If conversion fails, save as-is and hope it's already WAV
            wav_data = audio_data

        # Save audio
        audio_path = voice_dir / "audio.wav"
        audio_path.write_bytes(wav_data)

        # Calculate duration
        duration = get_audio_duration(wav_data)
        if duration:
            print(f"Audio duration: {duration:.2f}s")

        # Save transcription if available
        has_transcription = False
        if transcription:
            trans_path = voice_dir / "transcription.txt"
            trans_path.write_text(transcription, encoding="utf-8")
            has_transcription = True

        # Save metadata
        metadata = {
            "id": voice_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "has_transcription": has_transcription,
            "duration": duration
        }

        meta_path = voice_dir / "metadata.json"
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return metadata

    def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """
        Get voice sample metadata

        Args:
            voice_id: Voice UUID

        Returns:
            Voice metadata or None if not found
        """
        voice_dir = self.voices_dir / voice_id
        meta_path = voice_dir / "metadata.json"

        if not meta_path.exists():
            return None

        return json.loads(meta_path.read_text(encoding="utf-8"))

    def get_voice_audio_path(self, voice_id: str) -> Optional[Path]:
        """
        Get path to voice audio file

        Args:
            voice_id: Voice UUID

        Returns:
            Path to audio file or None if not found
        """
        audio_path = self.voices_dir / voice_id / "audio.wav"
        return audio_path if audio_path.exists() else None

    def get_voice_transcription(self, voice_id: str) -> Optional[str]:
        """
        Get voice transcription text

        Args:
            voice_id: Voice UUID

        Returns:
            Transcription text or None if not available
        """
        trans_path = self.voices_dir / voice_id / "transcription.txt"
        if not trans_path.exists():
            return None

        return trans_path.read_text(encoding="utf-8")

    def update_voice_transcription(self, voice_id: str, transcription: str) -> bool:
        """
        Update voice transcription

        Args:
            voice_id: Voice UUID
            transcription: Transcription text

        Returns:
            True if successful, False if voice not found
        """
        voice_dir = self.voices_dir / voice_id
        if not voice_dir.exists():
            return False

        # Save transcription
        trans_path = voice_dir / "transcription.txt"
        trans_path.write_text(transcription, encoding="utf-8")

        # Update metadata
        meta_path = voice_dir / "metadata.json"
        if meta_path.exists():
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            metadata["has_transcription"] = True
            meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return True

    def list_voices(self) -> List[Dict[str, Any]]:
        """
        List all voice samples with metadata

        Returns:
            List of voice metadata dictionaries, sorted by creation date (newest first)
        """
        voices = []
        for voice_dir in self.voices_dir.iterdir():
            if voice_dir.is_dir():
                meta_path = voice_dir / "metadata.json"
                if meta_path.exists():
                    voices.append(json.loads(meta_path.read_text(encoding="utf-8")))

        return sorted(voices, key=lambda v: v["created_at"], reverse=True)

    def delete_voice(self, voice_id: str) -> bool:
        """
        Delete voice sample and all associated files

        Args:
            voice_id: Voice UUID

        Returns:
            True if successful, False if voice not found
        """
        voice_dir = self.voices_dir / voice_id
        if not voice_dir.exists():
            return False

        shutil.rmtree(voice_dir)
        return True

    def create_generation(
        self,
        audio_data: bytes,
        text: str,
        voice_id: str,
        model: str,
        duration: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Save a TTS generation

        Args:
            audio_data: Raw audio file bytes (WAV format)
            text: Generated text
            voice_id: Reference voice UUID
            model: Model name used for generation
            duration: Audio duration in seconds

        Returns:
            Generation metadata dictionary
        """
        generation_id = str(uuid.uuid4())
        gen_dir = self.generations_dir / generation_id
        gen_dir.mkdir(parents=True, exist_ok=True)

        # Save audio
        audio_path = gen_dir / "audio.wav"
        audio_path.write_bytes(audio_data)

        # Save metadata
        metadata = {
            "id": generation_id,
            "text": text,
            "voice_id": voice_id,
            "model": model,
            "created_at": datetime.now().isoformat(),
            "duration": duration
        }

        meta_path = gen_dir / "metadata.json"
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return metadata

    def get_generation(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get generation metadata

        Args:
            generation_id: Generation UUID

        Returns:
            Generation metadata or None if not found
        """
        gen_dir = self.generations_dir / generation_id
        meta_path = gen_dir / "metadata.json"

        if not meta_path.exists():
            return None

        return json.loads(meta_path.read_text(encoding="utf-8"))

    def get_generation_audio_path(self, generation_id: str) -> Optional[Path]:
        """
        Get path to generation audio file

        Args:
            generation_id: Generation UUID

        Returns:
            Path to audio file or None if not found
        """
        audio_path = self.generations_dir / generation_id / "audio.wav"
        return audio_path if audio_path.exists() else None

    def list_generations(self, voice_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all TTS generations

        Args:
            voice_id: Optional filter by voice UUID

        Returns:
            List of generation metadata dictionaries, sorted by creation date (newest first)
        """
        generations = []
        for gen_dir in self.generations_dir.iterdir():
            if gen_dir.is_dir():
                meta_path = gen_dir / "metadata.json"
                if meta_path.exists():
                    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
                    # Filter by voice_id if provided
                    if voice_id is None or metadata.get("voice_id") == voice_id:
                        generations.append(metadata)

        return sorted(generations, key=lambda g: g["created_at"], reverse=True)

    def delete_generation(self, generation_id: str) -> bool:
        """
        Delete generation and all associated files

        Args:
            generation_id: Generation UUID

        Returns:
            True if successful, False if generation not found
        """
        gen_dir = self.generations_dir / generation_id
        if not gen_dir.exists():
            return False

        shutil.rmtree(gen_dir)
        return True


# Singleton instance
storage_service = StorageService()
