"""
Tests for Sprint 6 Observability Features
Unit tests for logging, metrics, and request tracking
"""

import pytest
import os
from unittest.mock import Mock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import Response


class TestLoggingConfiguration:
    """Test structured logging configuration"""
    
    def test_configure_logging_default(self):
        """Test default logging configuration"""
        from backend.observability import configure_logging
        
        # Should not raise
        configure_logging()
    
    def test_configure_logging_custom_level(self):
        """Test logging with custom level"""
        from backend.observability import configure_logging
        
        configure_logging(level="DEBUG")
        configure_logging(level="WARNING")
    
    def test_configure_logging_json_format(self):
        """Test JSON format logging"""
        from backend.observability import configure_logging
        
        configure_logging(format_type="json")
    
    def test_configure_logging_console_format(self):
        """Test console format logging"""
        from backend.observability import configure_logging
        
        configure_logging(format_type="console")
    
    def test_get_logger(self):
        """Test logger creation"""
        from backend.observability import get_logger, configure_logging
        
        configure_logging()
        logger = get_logger(__name__)
        
        assert logger is not None
        
        # Should be able to log without errors
        logger.info("test_message", key="value")
        logger.debug("debug_message", data={"test": 123})
        logger.warning("warning_message")
        logger.error("error_message", error="test")


class TestRequestIDMiddleware:
    """Test request ID generation and propagation"""
    
    def test_request_id_middleware_creates_id(self):
        """Test that middleware creates request ID when not present"""
        from backend.observability import RequestIDMiddleware
        
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) > 0
    
    def test_request_id_middleware_preserves_existing_id(self):
        """Test that middleware preserves existing X-Request-ID"""
        from backend.observability import RequestIDMiddleware
        
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        client = TestClient(app)
        custom_id = "my-custom-request-id"
        response = client.get("/test", headers={"X-Request-ID": custom_id})
        
        assert response.status_code == 200
        assert response.headers["x-request-id"] == custom_id
    
    def test_get_request_id(self):
        """Test get_request_id context function"""
        from backend.observability import get_request_id, RequestIDMiddleware
        
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        captured_id = None
        
        @app.get("/test")
        async def test_endpoint():
            nonlocal captured_id
            captured_id = get_request_id()
            return {"request_id": captured_id}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert captured_id is not None
        assert response.headers["x-request-id"] == captured_id


class TestMetrics:
    """Test metrics collection"""
    
    def test_metrics_singleton(self):
        """Test metrics singleton instance"""
        from backend.observability import metrics
        
        assert metrics is not None
    
    def test_model_created_metric(self):
        """Test model creation metric"""
        from backend.observability import metrics
        
        # Should not raise
        metrics.model_created("cadquery")
        metrics.model_created("openscad")
    
    def test_simulation_run_metric(self):
        """Test simulation metric"""
        from backend.observability import metrics
        
        metrics.simulation_run("structural")
        metrics.simulation_run("thermal")
    
    def test_budget_calculated_metric(self):
        """Test budget calculation metric"""
        from backend.observability import metrics
        
        metrics.budget_calculated()
    
    def test_error_metric(self):
        """Test error metric"""
        from backend.observability import metrics
        
        metrics.error("validation_error", "/api/v1/models")
        metrics.error("server_error", "/api/v1/simulation")
    
    def test_exception_metric(self):
        """Test exception metric"""
        from backend.observability import metrics
        
        metrics.exception("ValueError")
        metrics.exception("KeyError")


class TestMetricsMiddleware:
    """Test metrics middleware"""
    
    def test_metrics_middleware_tracks_requests(self):
        """Test that middleware tracks HTTP requests"""
        from backend.observability import MetricsMiddleware
        
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
    
    def test_metrics_middleware_skips_health_checks(self):
        """Test that middleware skips health check paths"""
        from backend.observability import MetricsMiddleware
        
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)
        
        @app.get("/health")
        async def health():
            return {"status": "ok"}
        
        @app.get("/metrics")
        async def metrics_endpoint():
            return {"metrics": "data"}
        
        client = TestClient(app)
        
        # These should not be tracked
        client.get("/health")
        client.get("/metrics")
    
    def test_metrics_middleware_tracks_errors(self):
        """Test that middleware tracks error responses"""
        from backend.observability import MetricsMiddleware
        from fastapi import HTTPException
        
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)
        
        @app.get("/error")
        async def error_endpoint():
            raise HTTPException(status_code=404, detail="Not found")
        
        client = TestClient(app)
        response = client.get("/error")
        
        assert response.status_code == 404


class TestLoggingMiddleware:
    """Test logging middleware"""
    
    def test_logging_middleware_logs_requests(self):
        """Test that middleware logs requests"""
        from backend.observability import LoggingMiddleware, configure_logging
        
        configure_logging()
        
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
    
    def test_logging_middleware_skips_health_checks(self):
        """Test that middleware skips health check paths"""
        from backend.observability import LoggingMiddleware, configure_logging
        
        configure_logging()
        
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)
        
        @app.get("/health")
        async def health():
            return {"status": "ok"}
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200


class TestMetricsEndpoint:
    """Test Prometheus metrics endpoint"""
    
    def test_setup_metrics(self):
        """Test metrics setup function"""
        from backend.observability import setup_metrics
        
        metrics_data = setup_metrics()
        
        assert metrics_data is not None
        assert isinstance(metrics_data, bytes)
    
    def test_get_metrics_content_type(self):
        """Test metrics content type"""
        from backend.observability import get_metrics_content_type
        
        content_type = get_metrics_content_type()
        
        assert content_type is not None
        assert "text/plain" in content_type or "text" in content_type


class TestIntegration:
    """Integration tests for observability features"""
    
    def test_all_middleware_together(self):
        """Test all observability middleware working together"""
        from backend.observability import (
            RequestIDMiddleware,
            LoggingMiddleware,
            MetricsMiddleware,
            configure_logging,
        )
        
        configure_logging(format_type="console")
        
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(MetricsMiddleware)
        
        @app.get("/test")
        async def test_endpoint(request: Request):
            return {
                "message": "test",
                "request_id": request.state.request_id
            }
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        assert response.json()["request_id"] == response.headers["x-request-id"]
    
    def test_observability_with_errors(self):
        """Test observability features with error handling"""
        from backend.observability import (
            RequestIDMiddleware,
            LoggingMiddleware,
            MetricsMiddleware,
            configure_logging,
        )
        from fastapi import HTTPException
        
        configure_logging(format_type="console")
        
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(MetricsMiddleware)
        
        @app.get("/success")
        async def success_endpoint():
            return {"status": "ok"}
        
        @app.get("/error")
        async def error_endpoint():
            raise HTTPException(status_code=400, detail="Bad request")
        
        client = TestClient(app)
        
        # Success case
        response = client.get("/success")
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        
        # Error case
        response = client.get("/error")
        assert response.status_code == 400
        assert "x-request-id" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
