"""
Unit tests for __main__ module.

Run with: pytest tests/test_main.py -v
"""

import subprocess
import sys


class TestModuleExecution:
    """Tests for module execution."""

    def test_module_runnable(self):
        """Module should be runnable with python -m."""
        result = subprocess.run(
            [sys.executable, "-m", "nobu", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "0.1.0" in result.stdout

    def test_module_help(self):
        """Module help should work."""
        result = subprocess.run(
            [sys.executable, "-m", "nobu", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "scan" in result.stdout
        assert "profile" in result.stdout

    def test_module_scan_help(self):
        """Scan help should work."""
        result = subprocess.run(
            [sys.executable, "-m", "nobu", "scan", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "--target" in result.stdout
        assert "--ports" in result.stdout

    def test_module_profile_help(self):
        """Profile help should work."""
        result = subprocess.run(
            [sys.executable, "-m", "nobu", "profile", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "fast" in result.stdout

    def test_module_scan_execution(self):
        """Scan execution should work."""
        result = subprocess.run(
            [
                sys.executable, "-m", "nobu", "scan",
                "--target", "127.0.0.1",
                "--ports", "65432",
                "--timeout", "0.3",
                "--quiet",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0


class TestMainImport:
    """Tests for main module import."""

    def test_main_function_importable(self):
        """Main function should be importable."""
        from nobu.__main__ import main
        assert callable(main)
