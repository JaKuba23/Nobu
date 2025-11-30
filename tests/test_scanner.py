"""
Unit tests for scanner functionality.

Run with: pytest tests/ -v
"""

import pytest

from nobu.output import ScanResult
from nobu.scanner import PortScanner, ScanConfig, ScanStats


class TestScanConfig:
    """Tests for ScanConfig dataclass."""

    def test_valid_config(self):
        """Valid configuration should initialize correctly."""
        config = ScanConfig(
            targets=["192.168.1.1"],
            ports=[80, 443],
            threads=100,
            timeout=1.0,
        )
        assert config.targets == ["192.168.1.1"]
        assert config.ports == [80, 443]
        assert config.threads == 100
        assert config.timeout == 1.0

    def test_default_values(self):
        """Default values should be set correctly."""
        config = ScanConfig(
            targets=["localhost"],
            ports=[80],
        )
        assert config.threads == 100
        assert config.timeout == 1.0
        assert config.banner_grab is False
        assert config.show_closed is False

    def test_empty_targets_raises(self):
        """Empty targets list should raise ValueError."""
        with pytest.raises(ValueError, match="target"):
            ScanConfig(targets=[], ports=[80])

    def test_empty_ports_raises(self):
        """Empty ports list should raise ValueError."""
        with pytest.raises(ValueError, match="port"):
            ScanConfig(targets=["localhost"], ports=[])

    def test_invalid_threads_raises(self):
        """Invalid thread count should raise ValueError."""
        with pytest.raises(ValueError, match="Thread"):
            ScanConfig(targets=["localhost"], ports=[80], threads=0)

    def test_invalid_timeout_raises(self):
        """Invalid timeout should raise ValueError."""
        with pytest.raises(ValueError, match="Timeout"):
            ScanConfig(targets=["localhost"], ports=[80], timeout=-1)


class TestScanStats:
    """Tests for ScanStats dataclass."""

    def test_initial_values(self):
        """Initial statistics should be zero."""
        stats = ScanStats()
        assert stats.total_ports == 0
        assert stats.open_ports == 0
        assert stats.closed_ports == 0
        assert stats.filtered_ports == 0
        assert stats.hosts_scanned == 0

    def test_update_open(self):
        """Update with open port should increment correctly."""
        stats = ScanStats()
        result = ScanResult(port=80, state="open")
        stats.update(result)

        assert stats.total_ports == 1
        assert stats.open_ports == 1
        assert stats.closed_ports == 0

    def test_update_closed(self):
        """Update with closed port should increment correctly."""
        stats = ScanStats()
        result = ScanResult(port=80, state="closed")
        stats.update(result)

        assert stats.total_ports == 1
        assert stats.closed_ports == 1
        assert stats.open_ports == 0

    def test_update_filtered(self):
        """Update with filtered port should increment correctly."""
        stats = ScanStats()
        result = ScanResult(port=80, state="filtered")
        stats.update(result)

        assert stats.total_ports == 1
        assert stats.filtered_ports == 1

    def test_duration_calculation(self):
        """Duration should calculate correctly."""
        stats = ScanStats()
        stats.start_time = 1000.0
        stats.end_time = 1005.5

        assert stats.duration == 5.5


class TestScanResult:
    """Tests for ScanResult dataclass."""

    def test_default_values(self):
        """Default values should be set correctly."""
        result = ScanResult(port=80, state="open")
        assert result.service == ""
        assert result.banner == ""
        assert result.response_time == 0.0

    def test_full_result(self):
        """Full result should store all values."""
        result = ScanResult(
            port=80,
            state="open",
            service="http",
            banner="Apache/2.4.41",
            response_time=0.05,
        )
        assert result.port == 80
        assert result.state == "open"
        assert result.service == "http"
        assert result.banner == "Apache/2.4.41"
        assert result.response_time == 0.05


class TestPortScanner:
    """Tests for PortScanner class."""

    def test_scanner_initialization(self):
        """Scanner should initialize with config."""
        config = ScanConfig(
            targets=["localhost"],
            ports=[80, 443],
        )
        scanner = PortScanner(config)

        assert scanner.config == config
        assert scanner._stop_flag is False

    def test_stop_flag(self):
        """Stop flag should be settable."""
        config = ScanConfig(
            targets=["localhost"],
            ports=[80],
        )
        scanner = PortScanner(config)

        assert scanner._stop_flag is False
        scanner.stop()
        assert scanner._stop_flag is True

    def test_decode_banner_utf8(self):
        """Banner decoder should handle UTF-8."""
        config = ScanConfig(targets=["localhost"], ports=[80])
        scanner = PortScanner(config)

        banner = scanner._decode_banner(b"Server: Apache/2.4.41\r\n")
        assert banner == "Server: Apache/2.4.41"

    def test_decode_banner_with_nulls(self):
        """Banner decoder should remove null bytes."""
        config = ScanConfig(targets=["localhost"], ports=[80])
        scanner = PortScanner(config)

        banner = scanner._decode_banner(b"Test\x00Banner\x00")
        assert "Test" in banner
        assert "\x00" not in banner

    def test_decode_banner_truncation(self):
        """Long banners should be truncated."""
        config = ScanConfig(targets=["localhost"], ports=[80])
        scanner = PortScanner(config)

        long_banner = b"A" * 200
        banner = scanner._decode_banner(long_banner)
        assert len(banner) <= 100


class TestQuickScan:
    """Tests for quick_scan convenience function."""

    def test_quick_scan_returns_list(self):
        """quick_scan should return a list of results."""
        from nobu.scanner import quick_scan

        # Scan a port that's likely closed
        results = quick_scan("127.0.0.1", [65432], timeout=0.3, threads=1)

        assert isinstance(results, list)
        assert len(results) == 1

    def test_quick_scan_sorted_results(self):
        """quick_scan results should be sorted by port."""
        from nobu.scanner import quick_scan

        results = quick_scan("127.0.0.1", [65432, 65431, 65433], timeout=0.3, threads=1)

        assert len(results) == 3
        assert results[0].port == 65431
        assert results[1].port == 65432
        assert results[2].port == 65433


class TestPortScannerAdvanced:
    """Advanced tests for PortScanner."""

    def test_scan_port_closed(self):
        """Scanning a closed port should return closed state."""
        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[65432],
            timeout=0.3,
        )
        scanner = PortScanner(config)
        result = scanner.scan_port("127.0.0.1", 65432)

        assert result.port == 65432
        assert result.state in ("closed", "filtered")

    def test_scan_port_timeout(self):
        """Timeout should be respected."""
        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[65432],
            timeout=0.1,
        )
        scanner = PortScanner(config)
        result = scanner.scan_port("127.0.0.1", 65432)

        # Should complete quickly
        assert result.response_time < 1.0

    def test_scan_host_multiple_ports(self):
        """Scanning multiple ports should return all results."""
        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[65431, 65432, 65433],
            timeout=0.3,
            threads=3,
        )
        scanner = PortScanner(config)
        results = list(scanner.scan_host("127.0.0.1"))

        assert len(results) == 3

    def test_scanner_with_banner_grab(self):
        """Banner grab config should be stored."""
        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[80],
            banner_grab=True,
        )
        scanner = PortScanner(config)

        assert scanner.config.banner_grab is True

    def test_decode_banner_multiline(self):
        """Banner decoder should handle multiline responses."""
        config = ScanConfig(targets=["localhost"], ports=[80])
        scanner = PortScanner(config)

        banner = scanner._decode_banner(b"Line1\nLine2\nLine3")
        # Should only return first line
        assert "Line1" in banner
        assert "\n" not in banner

    def test_decode_banner_empty(self):
        """Empty banner should return empty string."""
        config = ScanConfig(targets=["localhost"], ports=[80])
        scanner = PortScanner(config)

        banner = scanner._decode_banner(b"")
        assert banner == ""

    def test_scan_all_single_target(self):
        """scan_all should work with single target."""
        config = ScanConfig(
            targets=["127.0.0.1"],
            ports=[65432],
            timeout=0.3,
        )
        scanner = PortScanner(config)

        results_list = list(scanner.scan_all())
        assert len(results_list) == 1
        host, results = results_list[0]
        assert host == "127.0.0.1"
        assert len(results) == 1
