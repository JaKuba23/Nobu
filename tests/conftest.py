"""
Shared pytest fixtures and configuration for Nobu tests.
"""

import pytest
from unittest.mock import Mock

from nobu.output import ScanResult


@pytest.fixture
def mock_socket():
    """Mock socket for testing."""
    socket_mock = Mock()
    socket_mock.AF_INET = 2
    socket_mock.SOCK_STREAM = 1
    socket_mock.connect_ex.return_value = 0  # Connection successful
    socket_mock.gettimeout.return_value = 1.0
    return socket_mock


@pytest.fixture
def sample_scan_result():
    """Sample ScanResult for testing."""
    return ScanResult(
        port=80,
        state="open",
        service="http",
        banner="Apache/2.4.41",
        response_time=0.025
    )


@pytest.fixture
def closed_scan_result():
    """Closed port ScanResult for testing."""
    return ScanResult(
        port=65432,
        state="closed",
        service="unknown",
        response_time=0.001
    )
