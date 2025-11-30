"""
Unit tests for utility functions.

Run with: pytest tests/ -v
"""

import pytest

from nobu.utils import (
    COMMON_PORTS,
    format_duration,
    get_service_name,
    is_private_ip,
    parse_ports,
    parse_target,
    resolve_hostname,
    validate_threads,
    validate_timeout,
)


class TestParsePorts:
    """Tests for port parsing function."""

    def test_single_port(self):
        """Parse a single port number."""
        assert parse_ports("80") == [80]
        assert parse_ports("443") == [443]

    def test_port_range(self):
        """Parse a port range."""
        result = parse_ports("20-25")
        assert result == [20, 21, 22, 23, 24, 25]

    def test_port_list(self):
        """Parse comma-separated port list."""
        result = parse_ports("22,80,443")
        assert result == [22, 80, 443]

    def test_mixed_format(self):
        """Parse mixed format with ranges and individual ports."""
        result = parse_ports("22,80-82,443")
        assert result == [22, 80, 81, 82, 443]

    def test_removes_duplicates(self):
        """Duplicate ports should be removed."""
        result = parse_ports("80,80,443,80")
        assert result == [80, 443]

    def test_sorts_result(self):
        """Result should be sorted."""
        result = parse_ports("443,22,80")
        assert result == [22, 80, 443]

    def test_handles_whitespace(self):
        """Whitespace should be ignored."""
        result = parse_ports("22, 80, 443")
        assert result == [22, 80, 443]

    def test_empty_string_raises(self):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            parse_ports("")

    def test_invalid_port_number_raises(self):
        """Invalid port number should raise ValueError."""
        with pytest.raises(ValueError):
            parse_ports("abc")

    def test_out_of_range_port_raises(self):
        """Port out of valid range should raise ValueError."""
        with pytest.raises(ValueError, match="65535"):
            parse_ports("70000")

        with pytest.raises(ValueError):
            parse_ports("0")

    def test_invalid_range_raises(self):
        """Invalid range format should raise ValueError."""
        with pytest.raises(ValueError):
            parse_ports("100-50")  # Start > end

    def test_large_range(self):
        """Large port range should work."""
        result = parse_ports("1-100")
        assert len(result) == 100
        assert result[0] == 1
        assert result[-1] == 100


class TestFormatDuration:
    """Tests for duration formatting function."""

    def test_milliseconds(self):
        """Sub-second durations show as milliseconds."""
        assert format_duration(0.5) == "500ms"
        assert format_duration(0.001) == "1ms"

    def test_seconds(self):
        """Durations under a minute show as seconds."""
        assert format_duration(1.5) == "1.50s"
        assert format_duration(45.123) == "45.12s"

    def test_minutes(self):
        """Durations under an hour show as minutes and seconds."""
        assert format_duration(90) == "1m 30.0s"
        assert format_duration(125.5) == "2m 5.5s"

    def test_hours(self):
        """Long durations show as hours and minutes."""
        assert format_duration(3661) == "1h 1m"
        assert format_duration(7200) == "2h 0m"


class TestValidateTimeout:
    """Tests for timeout validation."""

    def test_valid_timeout(self):
        """Valid timeout values should pass through."""
        assert validate_timeout(1.0) == 1.0
        assert validate_timeout(0.5) == 0.5
        assert validate_timeout(30) == 30

    def test_zero_timeout_raises(self):
        """Zero timeout should raise ValueError."""
        with pytest.raises(ValueError, match="positive"):
            validate_timeout(0)

    def test_negative_timeout_raises(self):
        """Negative timeout should raise ValueError."""
        with pytest.raises(ValueError, match="positive"):
            validate_timeout(-1)

    def test_excessive_timeout_raises(self):
        """Timeout over 30s should raise ValueError."""
        with pytest.raises(ValueError, match="30"):
            validate_timeout(60)


class TestValidateThreads:
    """Tests for thread count validation."""

    def test_valid_threads(self):
        """Valid thread counts should pass through."""
        assert validate_threads(1) == 1
        assert validate_threads(100) == 100
        assert validate_threads(1000) == 1000

    def test_zero_threads_raises(self):
        """Zero threads should raise ValueError."""
        with pytest.raises(ValueError, match="at least 1"):
            validate_threads(0)

    def test_excessive_threads_raises(self):
        """Over 1000 threads should raise ValueError."""
        with pytest.raises(ValueError, match="1000"):
            validate_threads(2000)


class TestIsPrivateIP:
    """Tests for private IP detection."""

    def test_private_ips(self):
        """Private IP addresses should return True."""
        assert is_private_ip("192.168.1.1") is True
        assert is_private_ip("10.0.0.1") is True
        assert is_private_ip("172.16.0.1") is True
        assert is_private_ip("127.0.0.1") is True

    def test_public_ips(self):
        """Public IP addresses should return False."""
        assert is_private_ip("8.8.8.8") is False

    def test_link_local_ip(self):
        """Link-local IP addresses should be detected as private."""
        assert is_private_ip("169.254.1.1") is True
        assert is_private_ip("1.1.1.1") is False
        assert is_private_ip("142.250.185.78") is False

    def test_invalid_ip(self):
        """Invalid IP should return False."""
        assert is_private_ip("invalid") is False
        assert is_private_ip("") is False


class TestGetServiceName:
    """Tests for service name lookup."""

    def test_common_services(self):
        """Common ports should return service names."""
        # These may vary by system, so just check they return something
        http = get_service_name(80)
        assert http in ("http", "www", "")

        ssh = get_service_name(22)
        assert ssh in ("ssh", "")

    def test_unknown_port(self):
        """Unknown ports should return empty string."""
        assert get_service_name(65432) == ""


class TestParseTarget:
    """Tests for target parsing function."""

    def test_single_ip(self):
        """Single IP should return list with one IP."""
        result = parse_target("192.168.1.1")
        assert result == ["192.168.1.1"]

    def test_localhost(self):
        """Localhost should be resolvable."""
        result = parse_target("127.0.0.1")
        assert result == ["127.0.0.1"]

    def test_cidr_small(self):
        """Small CIDR should expand to host list."""
        result = parse_target("192.168.1.0/30")
        assert len(result) == 2  # /30 has 2 usable hosts

    def test_cidr_24(self):
        """/24 CIDR should expand correctly."""
        result = parse_target("10.0.0.0/24")
        assert len(result) == 254  # /24 has 254 usable hosts

    def test_empty_target_raises(self):
        """Empty target should raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            parse_target("")

    def test_invalid_cidr_raises(self):
        """Invalid CIDR should raise ValueError."""
        with pytest.raises(ValueError):
            parse_target("192.168.1.1/99")


class TestResolveHostname:
    """Tests for hostname resolution."""

    def test_resolve_ip(self):
        """IP address should resolve to itself."""
        result = resolve_hostname("127.0.0.1")
        assert result == "127.0.0.1"

    def test_resolve_invalid_raises(self):
        """Invalid hostname should raise ValueError."""
        with pytest.raises(ValueError, match="Cannot resolve"):
            resolve_hostname("this.hostname.does.not.exist.invalid")


class TestCommonPorts:
    """Tests for common ports constants."""

    def test_top20_defined(self):
        """Top 20 ports should be defined."""
        assert "top20" in COMMON_PORTS
        assert len(COMMON_PORTS["top20"]) == 20

    def test_web_ports_defined(self):
        """Web ports should include 80 and 443."""
        assert "web" in COMMON_PORTS
        assert 80 in COMMON_PORTS["web"]
        assert 443 in COMMON_PORTS["web"]

    def test_database_ports_defined(self):
        """Database ports should include common databases."""
        assert "database" in COMMON_PORTS
        assert 3306 in COMMON_PORTS["database"]  # MySQL
        assert 5432 in COMMON_PORTS["database"]  # PostgreSQL
        assert 27017 in COMMON_PORTS["database"]  # MongoDB
