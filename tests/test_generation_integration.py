"""Integration tests for TTS generation (requires model download, runs slowly)."""
import pytest
import time
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestGenerationIntegration:
    """Integration tests for actual TTS generation.

    Run with: pytest tests/test_generation_integration.py -m integration -v

    Note: These tests require:
    - MLX backend (Mac with Apple Silicon)
    - Model download (~1.5-3.5GB on first run)
    - Several minutes to complete
    """

    def test_sync_generation_short_spanish_text(
        self, client: TestClient, created_voice: dict
    ):
        """Test synchronous TTS generation with short Spanish text."""
        voice_id = created_voice["id"]

        # Short Spanish sentence for testing
        test_text = "Buenos días, este es un breve mensaje de prueba."

        generation_request = {
            "text": test_text,
            "voice_id": voice_id,
            "model": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16"
        }

        print(f"\n🎙️  Starting synchronous generation...")
        print(f"📝 Text: {test_text}")
        print(f"🔊 Voice ID: {voice_id}")
        print(f"⏳ This may take 1-3 minutes on first run (model download)...")

        start_time = time.time()
        response = client.post("/api/generations", json=generation_request)
        elapsed = time.time() - start_time

        print(f"✅ Generation completed in {elapsed:.1f} seconds")

        # Verify response
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()

        # Verify generation metadata
        assert "id" in data
        assert data["text"] == test_text
        assert data["voice_id"] == voice_id
        assert "model" in data
        assert "created_at" in data
        assert "audio_url" in data
        assert "duration" in data

        generation_id = data["id"]
        print(f"📦 Generation ID: {generation_id}")
        print(f"⏱️  Audio duration: {data.get('duration', 'N/A')} seconds")
        print(f"🎵 Model used: {data['model']}")

        # Verify we can download the audio
        audio_response = client.get(f"/api/generations/{generation_id}/audio")
        assert audio_response.status_code == 200
        assert audio_response.headers["content-type"] == "audio/wav"

        audio_data = audio_response.content
        assert len(audio_data) > 0
        assert audio_data[:4] == b"RIFF"  # WAV file header

        print(f"🎧 Audio file size: {len(audio_data) / 1024:.1f} KB")
        print(f"✨ Test passed!")

    def test_async_generation_with_progress_tracking(
        self, client: TestClient, created_voice: dict
    ):
        """Test asynchronous TTS generation with progress tracking."""
        voice_id = created_voice["id"]

        # Another short Spanish sentence
        test_text = "La tecnología de clonación de voz es increíble."

        generation_request = {
            "text": test_text,
            "voice_id": voice_id,
            "model": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16"
        }

        print(f"\n🚀 Starting async generation with progress tracking...")
        print(f"📝 Text: {test_text}")

        # Start async generation
        start_response = client.post("/api/generations/async", json=generation_request)
        assert start_response.status_code == 202

        task_data = start_response.json()
        assert "task_id" in task_data
        assert "status_url" in task_data

        task_id = task_data["task_id"]
        print(f"🆔 Task ID: {task_id}")
        print(f"📊 Status URL: {task_data['status_url']}")

        # Poll for progress
        max_wait = 300  # 5 minutes max
        poll_interval = 2  # Check every 2 seconds
        start_time = time.time()
        last_status = None
        last_progress = -1

        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                pytest.fail(f"Generation timed out after {max_wait} seconds")

            # Get task status
            status_response = client.get(f"/api/generations/tasks/{task_id}")
            assert status_response.status_code == 200

            task_status = status_response.json()
            status = task_status["status"]
            progress = task_status["progress"]
            message = task_status["message"]

            # Print progress updates
            if status != last_status or progress != last_progress:
                print(f"⏳ [{elapsed:.1f}s] Status: {status} | Progress: {progress}% | {message}")
                last_status = status
                last_progress = progress

            # Check if completed
            if status == "completed":
                print(f"✅ Generation completed in {elapsed:.1f} seconds")

                # Verify result
                assert "result" in task_status
                result = task_status["result"]
                assert result is not None
                assert result["text"] == test_text
                assert result["voice_id"] == voice_id
                assert "audio_url" in result

                generation_id = result["id"]
                print(f"📦 Generation ID: {generation_id}")

                # Verify audio download
                audio_response = client.get(result["audio_url"])
                assert audio_response.status_code == 200
                assert audio_response.headers["content-type"] == "audio/wav"

                audio_data = audio_response.content
                assert len(audio_data) > 0
                print(f"🎧 Audio file size: {len(audio_data) / 1024:.1f} KB")
                print(f"✨ Async test passed!")

                break

            elif status == "failed":
                error = task_status.get("error", "Unknown error")
                pytest.fail(f"Generation failed: {error}")

            # Wait before next poll
            time.sleep(poll_interval)

    def test_generation_progress_stages(
        self, client: TestClient, created_voice: dict
    ):
        """Test that generation goes through expected progress stages."""
        voice_id = created_voice["id"]
        test_text = "Probando las diferentes etapas del proceso."

        # Start async generation
        start_response = client.post("/api/generations/async", json={
            "text": test_text,
            "voice_id": voice_id,
            "model": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16"
        })
        assert start_response.status_code == 202

        task_id = start_response.json()["task_id"]
        print(f"\n📊 Tracking progress stages for task {task_id}...")

        # Track which stages we've seen
        seen_stages = set()
        expected_stages = {"pending", "initializing", "generating", "processing", "completed"}

        max_wait = 300
        start_time = time.time()

        while True:
            if time.time() - start_time > max_wait:
                pytest.fail("Timeout waiting for completion")

            status_response = client.get(f"/api/generations/tasks/{task_id}")
            task_status = status_response.json()
            status = task_status["status"]

            seen_stages.add(status)

            if status == "completed":
                print(f"✅ Completed!")
                print(f"📋 Stages observed: {', '.join(sorted(seen_stages))}")

                # We should have seen most stages (though some may be too fast to catch)
                assert "completed" in seen_stages
                # At minimum we should see pending/initializing and completed
                assert len(seen_stages) >= 2

                break
            elif status == "failed":
                pytest.fail(f"Generation failed: {task_status.get('error')}")

            time.sleep(1)

