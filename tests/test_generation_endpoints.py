"""Tests for TTS generation endpoints."""
import pytest
from fastapi.testclient import TestClient


class TestGenerationEndpoints:
    """Test suite for /api/generations endpoints."""

    def test_create_generation(
        self, client: TestClient, created_voice: dict
    ):
        """Test creating a TTS generation."""
        pytest.skip("TTS generation requires model download and takes significant time")

        voice_id = created_voice["id"]
        generation_request = {
            "text": "Hola, esto es una prueba de generación de voz.",
            "voice_id": voice_id
        }

        response = client.post("/api/generations", json=generation_request)

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["text"] == generation_request["text"]
        assert data["voice_id"] == voice_id
        assert "model" in data
        assert "created_at" in data
        assert "audio_url" in data

    def test_create_generation_with_model(
        self, client: TestClient, created_voice: dict
    ):
        """Test creating a TTS generation with specific model."""
        pytest.skip("TTS generation requires model download and takes significant time")

        voice_id = created_voice["id"]
        generation_request = {
            "text": "Esta es una prueba con un modelo específico.",
            "voice_id": voice_id,
            "model": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16"
        }

        response = client.post("/api/generations", json=generation_request)

        assert response.status_code == 201
        data = response.json()
        assert data["model"] == generation_request["model"]

    def test_create_generation_missing_text(
        self, client: TestClient, created_voice: dict
    ):
        """Test creating generation without text fails."""
        generation_request = {
            "voice_id": created_voice["id"]
        }

        response = client.post("/api/generations", json=generation_request)

        assert response.status_code == 422  # Validation error

    def test_create_generation_missing_voice_id(self, client: TestClient):
        """Test creating generation without voice_id fails."""
        generation_request = {
            "text": "Test text"
        }

        response = client.post("/api/generations", json=generation_request)

        assert response.status_code == 422  # Validation error

    def test_create_generation_empty_text(
        self, client: TestClient, created_voice: dict
    ):
        """Test creating generation with empty text fails."""
        generation_request = {
            "text": "",
            "voice_id": created_voice["id"]
        }

        response = client.post("/api/generations", json=generation_request)

        assert response.status_code == 422  # Validation error

    def test_create_generation_text_too_long(
        self, client: TestClient, created_voice: dict
    ):
        """Test creating generation with text exceeding max length."""
        # Create text longer than 5000 characters
        long_text = "A" * 5001

        generation_request = {
            "text": long_text,
            "voice_id": created_voice["id"]
        }

        response = client.post("/api/generations", json=generation_request)

        assert response.status_code == 422  # Validation error

    def test_create_generation_voice_not_found(self, client: TestClient):
        """Test creating generation with non-existent voice fails."""
        generation_request = {
            "text": "Test text",
            "voice_id": "non-existent-voice-id"
        }

        response = client.post("/api/generations", json=generation_request)

        assert response.status_code == 404

    def test_create_generation_voice_without_transcription(
        self, client: TestClient, voice_sample_path
    ):
        """Test creating generation with voice that has no transcription."""
        # Create voice without transcription
        with open(voice_sample_path, "rb") as f:
            voice_response = client.post(
                "/api/voices",
                files={"audio": ("voice.wav", f, "audio/wav")},
                data={"name": "No Transcription", "auto_transcribe": "false"}
            )

        voice_id = voice_response.json()["id"]

        generation_request = {
            "text": "Test text",
            "voice_id": voice_id
        }

        response = client.post("/api/generations", json=generation_request)

        # Should fail because voice has no transcription
        assert response.status_code == 400

    def test_list_generations_empty(self, client: TestClient):
        """Test listing generations when none exist."""
        response = client.get("/api/generations")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_generations_with_filter(
        self, client: TestClient, created_voice: dict
    ):
        """Test listing generations filtered by voice_id."""
        pytest.skip("Requires generation to be created first")

        voice_id = created_voice["id"]

        # List with filter
        response = client.get(f"/api/generations?voice_id={voice_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # All returned generations should be for this voice
        for generation in data:
            assert generation["voice_id"] == voice_id

    def test_get_generation_by_id(self, client: TestClient):
        """Test retrieving a specific generation by ID."""
        pytest.skip("Requires generation to be created first")

        # This would need a created generation
        # generation_id = created_generation["id"]
        # response = client.get(f"/api/generations/{generation_id}")
        # assert response.status_code == 200

    def test_get_generation_not_found(self, client: TestClient):
        """Test retrieving a non-existent generation returns 404."""
        response = client.get("/api/generations/non-existent-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_generation_audio(self, client: TestClient):
        """Test downloading generation audio file."""
        pytest.skip("Requires generation to be created first")

        # generation_id = created_generation["id"]
        # response = client.get(f"/api/generations/{generation_id}/audio")
        # assert response.status_code == 200
        # assert response.headers["content-type"] == "audio/wav"

    def test_get_generation_audio_not_found(self, client: TestClient):
        """Test downloading audio for non-existent generation returns 404."""
        response = client.get("/api/generations/non-existent-id/audio")

        assert response.status_code == 404

    def test_delete_generation(self, client: TestClient):
        """Test deleting a generation."""
        pytest.skip("Requires generation to be created first")

        # generation_id = created_generation["id"]
        # delete_response = client.delete(f"/api/generations/{generation_id}")
        # assert delete_response.status_code == 204

        # # Verify it's gone
        # get_response = client.get(f"/api/generations/{generation_id}")
        # assert get_response.status_code == 404

    def test_delete_generation_not_found(self, client: TestClient):
        """Test deleting a non-existent generation returns 404."""
        response = client.delete("/api/generations/non-existent-id")

        assert response.status_code == 404

