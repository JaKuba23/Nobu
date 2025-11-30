"""
Docker integration tests for Nobu port scanner.

These tests require Docker to be running and will:
1. Start the docker-lab containers
2. Run scans against them
3. Verify results
4. Stop containers

Run with: pytest tests/test_docker_integration.py -v
Skip with: pytest tests/ -v --ignore=tests/test_docker_integration.py
"""

import json
import os
import subprocess
import time

import pytest

# Check if Docker is available
DOCKER_AVAILABLE = False
try:
    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        timeout=5,
    )
    DOCKER_AVAILABLE = result.returncode == 0
except (subprocess.TimeoutExpired, FileNotFoundError):
    pass


@pytest.fixture(scope="module")
def docker_lab():
    """Start docker-lab containers for testing."""
    if not DOCKER_AVAILABLE:
        pytest.skip("Docker is not available")

    lab_dir = os.path.join(os.path.dirname(__file__), "..", "docker-lab")

    # Start containers
    subprocess.run(
        ["docker-compose", "up", "-d"],
        cwd=lab_dir,
        capture_output=True,
        check=True,
    )

    # Wait for services to start
    time.sleep(15)

    yield

    # Stop containers
    subprocess.run(
        ["docker-compose", "down"],
        cwd=lab_dir,
        capture_output=True,
    )


@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
class TestDockerIntegration:
    """Integration tests using Docker containers."""

    def test_nginx_port_open(self, docker_lab):
        """Test that Nginx port 8080 is detected as open."""
        from nobu.scanner import PortScanner, ScanConfig

        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[8080],
            timeout=2.0,
        )
        scanner = PortScanner(config)
        results = list(scanner.scan_host("127.0.0.1"))

        assert len(results) == 1
        assert results[0].port == 8080
        assert results[0].state == "open"

    def test_mysql_port_open(self, docker_lab):
        """Test that MySQL port 3306 is detected as open."""
        from nobu.scanner import PortScanner, ScanConfig

        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[3306],
            timeout=2.0,
        )
        scanner = PortScanner(config)
        results = list(scanner.scan_host("127.0.0.1"))

        assert len(results) == 1
        assert results[0].port == 3306
        assert results[0].state == "open"

    def test_redis_port_open(self, docker_lab):
        """Test that Redis port 6379 is detected as open."""
        from nobu.scanner import PortScanner, ScanConfig

        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[6379],
            timeout=2.0,
        )
        scanner = PortScanner(config)
        results = list(scanner.scan_host("127.0.0.1"))

        assert len(results) == 1
        assert results[0].port == 6379
        assert results[0].state == "open"

    def test_lab_profile_all_ports(self, docker_lab):
        """Test scanning all lab ports."""
        from nobu.scanner import PortScanner, ScanConfig

        lab_ports = [21, 1025, 2222, 3306, 5432, 6379, 8025, 8080, 8081, 8443, 27017]

        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=lab_ports,
            timeout=2.0,
            threads=20,
        )
        scanner = PortScanner(config)
        results = list(scanner.scan_host("127.0.0.1"))

        # All ports should be detected
        assert len(results) == len(lab_ports)

        # Count open ports
        open_ports = [r for r in results if r.state == "open"]

        # At least 8 ports should be open (some may fail on different systems)
        assert len(open_ports) >= 8, f"Only {len(open_ports)} ports open"

    def test_banner_grabbing(self, docker_lab):
        """Test banner grabbing on HTTP port."""
        from nobu.scanner import PortScanner, ScanConfig

        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[8080],
            timeout=2.0,
            banner_grab=True,
        )
        scanner = PortScanner(config)
        results = list(scanner.scan_host("127.0.0.1"))

        assert len(results) == 1
        assert results[0].state == "open"
        # Banner should contain HTTP or nginx
        assert "HTTP" in results[0].banner or "nginx" in results[0].banner.lower()

    def test_ssh_banner(self, docker_lab):
        """Test SSH banner detection."""
        from nobu.scanner import PortScanner, ScanConfig

        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[2222],
            timeout=2.0,
            banner_grab=True,
        )
        scanner = PortScanner(config)
        results = list(scanner.scan_host("127.0.0.1"))

        assert len(results) == 1
        assert results[0].state == "open"
        # SSH banner should contain SSH version
        assert "SSH" in results[0].banner

    def test_json_export(self, docker_lab, tmp_path):
        """Test JSON export functionality."""
        from nobu.output import ScanResult, create_json_output

        results = [
            ScanResult(port=8080, state="open", service="http", banner="nginx"),
            ScanResult(port=3306, state="open", service="mysql"),
        ]

        output = create_json_output(results, "127.0.0.1", 1.5)

        assert output["target"] == "127.0.0.1"
        assert output["summary"]["open"] == 2
        assert len(output["results"]) == 2

        # Write to file
        output_file = tmp_path / "results.json"
        with open(output_file, "w") as f:
            json.dump(output, f)

        # Read back and verify
        with open(output_file) as f:
            loaded = json.load(f)

        assert loaded["target"] == "127.0.0.1"

    def test_closed_port_detection(self, docker_lab):
        """Test that closed ports are properly detected."""
        from nobu.scanner import PortScanner, ScanConfig

        # Port 9999 should not be open
        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[9999],
            timeout=1.0,
        )
        scanner = PortScanner(config)
        results = list(scanner.scan_host("127.0.0.1"))

        assert len(results) == 1
        assert results[0].port == 9999
        assert results[0].state in ("closed", "filtered")

    def test_scan_stats(self, docker_lab):
        """Test scan statistics collection."""
        from nobu.scanner import PortScanner, ScanConfig

        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[8080, 8081, 9999],  # 2 open, 1 closed
            timeout=2.0,
        )
        scanner = PortScanner(config)
        list(scanner.scan_host("127.0.0.1"))

        assert scanner.stats.total_ports == 3
        assert scanner.stats.open_ports >= 2  # At least nginx and apache


@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
class TestCLIWithDocker:
    """CLI integration tests with Docker."""

    def test_cli_scan_command(self, docker_lab):
        """Test CLI scan command."""
        from nobu.cli import main

        # Run scan (returns exit code)
        exit_code = main(
            ["scan", "--target", "127.0.0.1", "--ports", "8080", "--quiet"]
        )

        assert exit_code == 0

    def test_cli_profile_command(self, docker_lab):
        """Test CLI profile command."""
        from nobu.cli import main

        exit_code = main(["profile", "lab", "--target", "127.0.0.1", "--quiet"])

        assert exit_code == 0

    def test_cli_json_output(self, docker_lab, tmp_path):
        """Test CLI JSON output."""
        from nobu.cli import main

        output_file = tmp_path / "scan.json"

        exit_code = main(
            [
                "scan",
                "--target",
                "127.0.0.1",
                "--ports",
                "8080,3306",
                "--quiet",
                "--output",
                str(output_file),
            ]
        )

        assert exit_code == 0
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert data["target"] == "127.0.0.1"
        assert data["summary"]["total_ports"] == 2
