"""
Unit tests for CLI module.

Run with: pytest tests/test_cli.py -v
"""

import pytest

from nobu.cli import NobuCLI, PROFILES, main


class TestProfiles:
    """Tests for scan profiles."""

    def test_fast_profile_exists(self):
        """Fast profile should be defined."""
        assert "fast" in PROFILES
        assert len(PROFILES["fast"]["ports"]) == 97  # top100 minus duplicates

    def test_full_profile_exists(self):
        """Full profile should be defined."""
        assert "full" in PROFILES
        assert len(PROFILES["full"]["ports"]) == 1024

    def test_web_profile_exists(self):
        """Web profile should be defined."""
        assert "web" in PROFILES
        assert 80 in PROFILES["web"]["ports"]
        assert 443 in PROFILES["web"]["ports"]

    def test_database_profile_exists(self):
        """Database profile should be defined."""
        assert "database" in PROFILES
        assert 3306 in PROFILES["database"]["ports"]  # MySQL
        assert 5432 in PROFILES["database"]["ports"]  # PostgreSQL

    def test_mail_profile_exists(self):
        """Mail profile should be defined."""
        assert "mail" in PROFILES
        assert 25 in PROFILES["mail"]["ports"]  # SMTP

    def test_stealth_profile_exists(self):
        """Stealth profile should have low thread count."""
        assert "stealth" in PROFILES
        assert PROFILES["stealth"]["threads"] <= 10

    def test_lab_profile_exists(self):
        """Lab profile should be defined."""
        assert "lab" in PROFILES
        assert 8080 in PROFILES["lab"]["ports"]


class TestNobuCLI:
    """Tests for NobuCLI class."""

    def test_cli_initialization(self):
        """CLI should initialize properly."""
        cli = NobuCLI()
        assert cli.parser is not None
        assert cli.formatter is None
        assert cli.scanner is None
        assert cli._interrupted is False

    def test_cli_version(self, capsys):
        """Version command should work."""
        cli = NobuCLI()
        result = cli.run(["--version"])
        assert result == 0

        captured = capsys.readouterr()
        assert "0.1.0" in captured.out
        assert "Ghost of Tsushima" in captured.out

    def test_cli_help(self, capsys):
        """Help should display without error."""
        cli = NobuCLI()
        result = cli.run([])
        assert result == 0

    def test_cli_scan_missing_target(self, capsys):
        """Scan without target should fail."""
        cli = NobuCLI()
        with pytest.raises(SystemExit):
            cli.run(["scan"])

    def test_cli_profile_missing_target(self, capsys):
        """Profile without target should fail."""
        cli = NobuCLI()
        with pytest.raises(SystemExit):
            cli.run(["profile", "fast"])

    def test_format_profiles(self):
        """Profile formatting should work."""
        cli = NobuCLI()
        formatted = cli._format_profiles()
        assert "fast" in formatted
        assert "web" in formatted
        assert "database" in formatted


class TestMainFunction:
    """Tests for main entry point."""

    def test_main_with_version(self, capsys):
        """Main with --version should work."""
        result = main(["--version"])
        assert result == 0

    def test_main_with_help(self, capsys):
        """Main with no args should show help."""
        result = main([])
        assert result == 0

    def test_main_scan_invalid_target(self, capsys):
        """Main with invalid target should return error."""
        result = main(["scan", "--target", "invalid..host", "--ports", "80"])
        assert result == 1


class TestCLIErrorHandling:
    """Tests for CLI error handling."""

    def test_invalid_port_range(self, capsys):
        """Invalid port range should show error."""
        result = main(["scan", "--target", "127.0.0.1", "--ports", "abc"])
        assert result == 1

    def test_invalid_port_number(self, capsys):
        """Port out of range should show error."""
        result = main(["scan", "--target", "127.0.0.1", "--ports", "99999"])
        assert result == 1


class TestCLIScanExecution:
    """Tests for actual scan execution via CLI."""

    def test_scan_localhost_closed_port(self, capsys):
        """Scanning closed port should complete."""
        result = main([
            "scan",
            "--target", "127.0.0.1",
            "--ports", "65432",
            "--timeout", "0.3",
            "--quiet",
            "--no-color",
        ])
        assert result == 0

    def test_scan_with_threads(self, capsys):
        """Scanning with custom thread count should work."""
        result = main([
            "scan",
            "--target", "127.0.0.1",
            "--ports", "65432,65433",
            "--threads", "10",
            "--timeout", "0.3",
            "--quiet",
        ])
        assert result == 0

    def test_profile_fast_execution(self, capsys):
        """Fast profile should execute."""
        result = main([
            "profile", "fast",
            "--target", "127.0.0.1",
            "--quiet",
        ])
        # May fail due to network, but should not crash
        assert result in (0, 1)

    def test_scan_with_banner_flag(self, capsys):
        """Banner flag should be accepted."""
        result = main([
            "scan",
            "--target", "127.0.0.1",
            "--ports", "65432",
            "--banner",
            "--timeout", "0.3",
            "--quiet",
        ])
        assert result == 0


class TestCLIOutputFormats:
    """Tests for CLI output formats."""

    def test_no_color_flag(self, capsys):
        """No color flag should work."""
        result = main([
            "scan",
            "--target", "127.0.0.1",
            "--ports", "65432",
            "--no-color",
            "--quiet",
            "--timeout", "0.3",
        ])
        assert result == 0

    def test_quiet_flag(self, capsys):
        """Quiet flag should reduce output."""
        result = main([
            "scan",
            "--target", "127.0.0.1",
            "--ports", "65432",
            "--quiet",
            "--timeout", "0.3",
        ])
        assert result == 0

    def test_verbose_flag(self, capsys):
        """Verbose flag should work."""
        result = main([
            "scan",
            "--target", "127.0.0.1",
            "--ports", "65432",
            "--verbose",
            "--timeout", "0.3",
            "--quiet",
        ])
        assert result == 0


class TestCLIOutputExport:
    """Tests for output export functionality."""

    def test_json_output(self, tmp_path, capsys):
        """JSON output should create file."""
        output_file = tmp_path / "results.json"
        result = main([
            "scan",
            "--target", "127.0.0.1",
            "--ports", "65432",
            "--timeout", "0.3",
            "--quiet",
            "--output", str(output_file),
        ])
        assert result == 0
        assert output_file.exists()

        import json
        with open(output_file) as f:
            data = json.load(f)
        assert "target" in data
        assert "results" in data

    def test_csv_output(self, tmp_path, capsys):
        """CSV output should create file."""
        output_file = tmp_path / "results.csv"
        result = main([
            "scan",
            "--target", "127.0.0.1",
            "--ports", "65432",
            "--timeout", "0.3",
            "--quiet",
            "--output", str(output_file),
        ])
        assert result == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "port" in content
        assert "state" in content


class TestCLIProfileExecution:
    """Tests for profile execution."""

    def test_all_profiles_loadable(self):
        """All profiles should be loadable."""
        from nobu.cli import PROFILES

        for name, config in PROFILES.items():
            assert "ports" in config
            assert "threads" in config
            assert "timeout" in config
            assert "description" in config
            assert len(config["ports"]) > 0

    def test_profile_stealth_execution(self, capsys):
        """Stealth profile should execute."""
        result = main([
            "profile", "stealth",
            "--target", "127.0.0.1",
            "--quiet",
        ])
        assert result in (0, 1)

    def test_profile_database_execution(self, capsys):
        """Database profile should execute."""
        result = main([
            "profile", "database",
            "--target", "127.0.0.1",
            "--quiet",
        ])
        assert result in (0, 1)
