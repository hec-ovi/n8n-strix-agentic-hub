"""Tests for application wiring."""

import os
from tempfile import TemporaryDirectory

from src.main import create_app


def test_create_app_registers_expected_routes() -> None:
    """App factory should register the health and report routes."""
    with TemporaryDirectory() as artifacts_dir:
        previous_artifacts_dir = os.environ.get("ARTIFACTS_DIR")
        try:
            os.environ["ARTIFACTS_DIR"] = artifacts_dir
            app = create_app()
        finally:
            if previous_artifacts_dir is None:
                del os.environ["ARTIFACTS_DIR"]
            else:
                os.environ["ARTIFACTS_DIR"] = previous_artifacts_dir

    route_paths = {route.path for route in app.routes}

    assert "/health" in route_paths
    assert "/api/v1/report-jobs" in route_paths
    assert "/artifacts" in route_paths
