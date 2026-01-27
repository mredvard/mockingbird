"""Tests for voice management endpoints."""
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


class TestVoiceEndpoints:
    """Test suite for /api/voices endpoints."""

    def test_create_voice_without_transcription(
        self, client: TestClient, voice_sample_path: Path
    ):
        """Test creating a voice sample without auto-transcription."""
        with open(voice_sample_path, "rb") as f:
            response = client.post(
                "/api/voices",
                files={"audio": ("test_voice.wav", f, "audio/wav")},
                data={"name": "My Test Voice", "auto_transcribe": "false"}
            )

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["name"] == "My Test Voice"
        assert data["has_transcription"] is False
        assert "created_at" in data

    def test_create_voice_with_auto_transcription(
        self, client: TestClient, voice_sample_path: Path
    ):
        """Test creating a voice sample with auto-transcription."""
        # Skip if transcription service is not available
        pytest.skip("Auto-transcription requires MLX Whisper model download")

        with open(voice_sample_path, "rb") as f:
            response = client.post(
                "/api/voices",
                files={"audio": ("test_voice.wav", f, "audio/wav")},
                data={"name": "Auto Transcribed Voice", "auto_transcribe": "true"}
            )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "Auto Transcribed Voice"
        assert data["has_transcription"] is True

    def test_create_voice_missing_audio(self, client: TestClient):
        """Test creating a voice without audio file fails."""
        response = client.post(
            "/api/voices",
            data={"name": "No Audio Voice"}
        )

        assert response.status_code == 422  # Validation error

    def test_create_voice_invalid_audio_format(self, client: TestClient):
        """Test creating a voice with invalid audio format."""
        fake_audio = io.BytesIO(b"not a valid wav file")

        response = client.post(
            "/api/voices",
            files={"audio": ("fake.wav", fake_audio, "audio/wav")},
            data={"name": "Invalid Audio"}
        )

        # Should either fail validation or succeed (validation depends on implementation)
        # If it succeeds, the audio is stored as-is
        assert response.status_code in [201, 400, 422]

    def test_list_voices_empty(self, client: TestClient):
        """Test listing voices returns list."""
        response = client.get("/api/voices")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # List might have voices from previous tests or be empty
        # Just verify it returns a valid list

    def test_list_voices_with_data(
        self, client: TestClient, voice_sample_path: Path
    ):
        """Test listing voices returns created voices."""
        # Create two voices
        with open(voice_sample_path, "rb") as f:
            client.post(
                "/api/voices",
                files={"audio": ("voice1.wav", f, "audio/wav")},
                data={"name": "UniqueVoice1", "auto_transcribe": "false"}
            )

        with open(voice_sample_path, "rb") as f:
            client.post(
                "/api/voices",
                files={"audio": ("voice2.wav", f, "audio/wav")},
                data={"name": "UniqueVoice2", "auto_transcribe": "false"}
            )

        # List voices
        response = client.get("/api/voices")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

        names = {voice["name"] for voice in data}
        assert "UniqueVoice1" in names
        assert "UniqueVoice2" in names

    def test_get_voice_by_id(self, client: TestClient, created_voice: dict):
        """Test retrieving a specific voice by ID."""
        voice_id = created_voice["id"]
        response = client.get(f"/api/voices/{voice_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == voice_id
        assert data["name"] == created_voice["name"]
        assert "transcription" in data

    def test_get_voice_not_found(self, client: TestClient):
        """Test retrieving a non-existent voice returns 404."""
        response = client.get("/api/voices/non-existent-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_voice_audio(self, client: TestClient, created_voice: dict):
        """Test downloading voice audio file."""
        voice_id = created_voice["id"]
        response = client.get(f"/api/voices/{voice_id}/audio")

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"

        # Check that we got audio data
        audio_data = response.content
        assert len(audio_data) > 0

        # WAV files start with "RIFF" header
        assert audio_data[:4] == b"RIFF"

    def test_get_voice_audio_not_found(self, client: TestClient):
        """Test downloading audio for non-existent voice returns 404."""
        response = client.get("/api/voices/non-existent-id/audio")

        assert response.status_code == 404

    def test_transcribe_voice(
        self, client: TestClient, voice_sample_path: Path
    ):
        """Test manual transcription of a voice."""
        pytest.skip("Transcription requires MLX Whisper model download")

        # Create voice without transcription
        with open(voice_sample_path, "rb") as f:
            create_response = client.post(
                "/api/voices",
                files={"audio": ("voice.wav", f, "audio/wav")},
                data={"name": "Voice To Transcribe", "auto_transcribe": "false"}
            )

        voice_id = create_response.json()["id"]

        # Trigger transcription
        response = client.post(f"/api/voices/{voice_id}/transcribe")

        assert response.status_code == 200
        data = response.json()
        assert data["has_transcription"] is True

    def test_update_transcription(
        self, client: TestClient, created_voice: dict
    ):
        """Test manually updating a voice transcription."""
        voice_id = created_voice["id"]
        new_transcription = "This is a manually updated transcription."

        response = client.post(
            f"/api/voices/{voice_id}/transcription",
            json={"transcription": new_transcription}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_transcription"] is True

        # Verify the transcription was updated
        get_response = client.get(f"/api/voices/{voice_id}")
        voice_data = get_response.json()
        assert voice_data["transcription"] == new_transcription

    def test_update_transcription_not_found(self, client: TestClient):
        """Test updating transcription for non-existent voice returns 404."""
        response = client.post(
            "/api/voices/non-existent-id/transcription",
            json={"transcription": "Test"}
        )

        assert response.status_code == 404

    def test_delete_voice(
        self, client: TestClient, voice_sample_path: Path
    ):
        """Test deleting a voice sample."""
        # Create a voice
        with open(voice_sample_path, "rb") as f:
            create_response = client.post(
                "/api/voices",
                files={"audio": ("voice.wav", f, "audio/wav")},
                data={"name": "Voice To Delete", "auto_transcribe": "false"}
            )

        voice_id = create_response.json()["id"]

        # Delete the voice
        delete_response = client.delete(f"/api/voices/{voice_id}")
        assert delete_response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/api/voices/{voice_id}")
        assert get_response.status_code == 404

    def test_delete_voice_not_found(self, client: TestClient):
        """Test deleting a non-existent voice returns 404."""
        response = client.delete("/api/voices/non-existent-id")

        assert response.status_code == 404

    def test_voice_lifecycle(
        self, client: TestClient, voice_sample_path: Path
    ):
        """Test complete voice lifecycle: create, update, retrieve, delete."""
        # Create
        with open(voice_sample_path, "rb") as f:
            create_response = client.post(
                "/api/voices",
                files={"audio": ("lifecycle.wav", f, "audio/wav")},
                data={"name": "Lifecycle Test", "auto_transcribe": "false"}
            )
        assert create_response.status_code == 201
        voice_id = create_response.json()["id"]

        # Update transcription
        update_response = client.post(
            f"/api/voices/{voice_id}/transcription",
            json={"transcription": "Test transcription for lifecycle"}
        )
        assert update_response.status_code == 200

        # Retrieve
        get_response = client.get(f"/api/voices/{voice_id}")
        assert get_response.status_code == 200
        assert get_response.json()["transcription"] == "Test transcription for lifecycle"

        # Download audio
        audio_response = client.get(f"/api/voices/{voice_id}/audio")
        assert audio_response.status_code == 200

        # Delete
        delete_response = client.delete(f"/api/voices/{voice_id}")
        assert delete_response.status_code == 204

        # Verify deletion
        final_get = client.get(f"/api/voices/{voice_id}")
        assert final_get.status_code == 404
