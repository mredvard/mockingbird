"""Test configuration and fixtures."""
import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import config


# Test transcription for voice_sample.wav
TEST_TRANSCRIPTION = """Chamo, a mí sí, todo bien. Después de que a Daniel lo sacaron de ingeniería, todo se regularizó. Los pagos caen el 10 de cada mes, el pingo ese no presionaba, chamo. Bueno, en sí la compañía no tiene una buena dirección. Es medio drama ahorita porque entregaron una vaina toda mal hecha y Denny, el CEO de ADECO, no le gustó nada. Y bueno, ya por lo menos hay gente hablando seriamente sobre eso. Ya Clubán va de salida, aunque todavía no concretan lo que van a hacer conmigo. Si me van a contratar o no me van a contratar. Entonces no sé. Vamos a ver. Tengo que hablar todo un minuto a ver cómo funciona este modelo, a ver si la transcripción, si el clonado de mi voz sale bien. Vamos a ver. Bueno, coño, realmente deben hacerlo self-service. Cada quien despliega su vaina, pero es chivo que esta es la tercera vez que hacen los mismos despliegues y no tomaron nada de notas. Vamos a ver."""


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Get the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def voice_sample_path(test_data_dir: Path) -> Path:
    """Get path to the voice sample WAV file."""
    sample_path = test_data_dir / "voice_sample.wav"
    if not sample_path.exists():
        pytest.skip(f"Voice sample not found at {sample_path}")
    return sample_path


@pytest.fixture(scope="function")
def temp_data_dir() -> Generator[Path, None, None]:
    """Create a temporary data directory for tests."""
    temp_dir = Path(tempfile.mkdtemp(prefix="tts_test_"))

    # Create subdirectories
    voices_dir = temp_dir / "voices"
    generations_dir = temp_dir / "generations"
    voices_dir.mkdir(parents=True)
    generations_dir.mkdir(parents=True)

    # Store original directories
    original_data_dir = config.DATA_DIR
    original_voices_dir = config.VOICES_DIR
    original_generations_dir = config.GENERATIONS_DIR

    # Override config data directories
    config.DATA_DIR = temp_dir
    config.VOICES_DIR = voices_dir
    config.GENERATIONS_DIR = generations_dir

    yield temp_dir

    # Restore original directories
    config.DATA_DIR = original_data_dir
    config.VOICES_DIR = original_voices_dir
    config.GENERATIONS_DIR = original_generations_dir

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def client(temp_data_dir: Path) -> TestClient:
    """Create a test client with temporary data directory."""
    # Force reload of services with new config
    from backend.app import services
    from backend.app.services.storage import StorageService

    # Create new storage service instance with updated config
    services.storage_service = StorageService()

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def sample_voice_data(voice_sample_path: Path) -> tuple[bytes, str]:
    """Load sample voice data and transcription."""
    with open(voice_sample_path, "rb") as f:
        audio_data = f.read()
    return audio_data, TEST_TRANSCRIPTION


@pytest.fixture(scope="function")
def created_voice(client: TestClient, voice_sample_path: Path) -> dict:
    """Create a test voice and return its data."""
    with open(voice_sample_path, "rb") as f:
        response = client.post(
            "/api/voices",
            files={"audio": ("voice_sample.wav", f, "audio/wav")},
            data={"name": "Test Voice", "auto_transcribe": "false"}
        )

    assert response.status_code == 201
    voice = response.json()

    # Add transcription manually
    transcribe_response = client.post(
        f"/api/voices/{voice['id']}/transcription",
        json={"transcription": TEST_TRANSCRIPTION}
    )
    assert transcribe_response.status_code == 200

    # Return updated voice data
    get_response = client.get(f"/api/voices/{voice['id']}")
    return get_response.json()
