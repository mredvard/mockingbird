"""Tests for models info and health check endpoints."""
import pytest
from fastapi.testclient import TestClient


class TestModelsEndpoints:
    """Test suite for /api/generations/models endpoints."""

    def test_get_backend_info(self, client: TestClient):
        """Test retrieving backend information."""
        response = client.get("/api/generations/models/info")

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert "platform" in data
        assert "available_models" in data
        assert "sample_rate" in data

        # Verify types
        assert isinstance(data["platform"], str)
        assert isinstance(data["available_models"], list)
        assert isinstance(data["sample_rate"], int)

        # Verify platform is either "mlx" or "pytorch"
        assert data["platform"] in ["mlx", "pytorch"]

        # Verify sample rate is reasonable (24000 Hz)
        assert data["sample_rate"] == 24000

        # Verify we have at least one model available
        assert len(data["available_models"]) > 0

    def test_backend_info_has_current_model(self, client: TestClient):
        """Test that backend info may include current_model."""
        response = client.get("/api/generations/models/info")

        assert response.status_code == 200
        data = response.json()

        # current_model is optional and may be None if no model loaded yet
        if "current_model" in data:
            assert isinstance(data["current_model"], (str, type(None)))

    def test_list_available_models(self, client: TestClient):
        """Test listing available models."""
        response = client.get("/api/generations/models/list")

        assert response.status_code == 200
        data = response.json()

        # Should return a list of model names
        assert isinstance(data, list)
        assert len(data) > 0

        # All items should be strings
        for model in data:
            assert isinstance(model, str)
            # Model names should be non-empty
            assert len(model) > 0

    def test_models_list_matches_info(self, client: TestClient):
        """Test that models list matches the available_models in info."""
        info_response = client.get("/api/generations/models/info")
        list_response = client.get("/api/generations/models/list")

        assert info_response.status_code == 200
        assert list_response.status_code == 200

        info_models = info_response.json()["available_models"]
        list_models = list_response.json()

        # The lists should be the same
        assert set(info_models) == set(list_models)

    def test_mlx_models_on_mac(self, client: TestClient):
        """Test that MLX models are available on Mac platform."""
        info_response = client.get("/api/generations/models/info")
        data = info_response.json()

        if data["platform"] == "mlx":
            # Should have MLX-specific models
            models = data["available_models"]
            assert any("mlx-community" in model for model in models)
            assert any("Qwen3-TTS" in model for model in models)


class TestHealthEndpoint:
    """Test suite for /api/health endpoint."""

    def test_health_check(self, client: TestClient):
        """Test basic health check."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_check_response_format(self, client: TestClient):
        """Test health check response format."""
        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert isinstance(data, dict)

    def test_health_check_multiple_requests(self, client: TestClient):
        """Test that health check is consistent across multiple requests."""
        responses = [client.get("/api/health") for _ in range(3)]

        for response in responses:
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"


class TestAPIRoot:
    """Test suite for API root and documentation endpoints."""

    def test_root_redirect_to_docs(self, client: TestClient):
        """Test that root redirects to API documentation."""
        response = client.get("/", follow_redirects=False)

        # Should redirect to /docs
        assert response.status_code in [200, 307, 308]

    def test_openapi_schema_available(self, client: TestClient):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()

        # Verify OpenAPI schema structure
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

        # Verify our endpoints are documented
        paths = data["paths"]
        # FastAPI may include trailing slashes
        assert any("/api/voices" in path for path in paths)
        assert any("/api/generations" in path for path in paths)
        assert "/api/health" in paths

    def test_docs_page_accessible(self, client: TestClient):
        """Test that Swagger UI docs page is accessible."""
        response = client.get("/docs")

        assert response.status_code == 200
        # Should return HTML page
        assert "text/html" in response.headers["content-type"]

    def test_redoc_page_accessible(self, client: TestClient):
        """Test that ReDoc docs page is accessible."""
        response = client.get("/redoc")

        assert response.status_code == 200
        # Should return HTML page
        assert "text/html" in response.headers["content-type"]


class TestCORS:
    """Test suite for CORS configuration."""

    def test_cors_headers_present(self, client: TestClient):
        """Test that CORS headers are present in responses."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )

        # CORS preflight response
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_frontend_origins(self, client: TestClient):
        """Test that CORS allows common frontend development origins."""
        origins = [
            "http://localhost:5173",
            "http://localhost:3000"
        ]

        for origin in origins:
            response = client.get(
                "/api/health",
                headers={"Origin": origin}
            )

            assert response.status_code == 200
            # Should have CORS header allowing the origin
            assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Test suite for error handling."""

    def test_404_not_found(self, client: TestClient):
        """Test that non-existent endpoints return 404."""
        response = client.get("/api/non-existent-endpoint")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_405_method_not_allowed(self, client: TestClient):
        """Test that wrong HTTP methods return 405."""
        # Health check only supports GET
        response = client.post("/api/health")

        assert response.status_code == 405
        data = response.json()
        assert "detail" in data

    def test_422_validation_error_format(self, client: TestClient):
        """Test that validation errors return proper format."""
        # Send invalid data to trigger validation error
        response = client.post(
            "/api/generations",
            json={"invalid": "data"}
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
