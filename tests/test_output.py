"""
Unit tests for output formatting functions.

Run with: pytest tests/ -v
"""

from nobu.output import (
    Colors,
    OutputFormatter,
    ScanResult,
    create_csv_output,
    create_json_output,
)


class TestColors:
    """Tests for Colors class."""

    def setup_method(self):
        """Reset colors before each test."""
        # Restore default color values
        Colors.RED = "\033[91m"
        Colors.GREEN = "\033[92m"
        Colors.YELLOW = "\033[93m"
        Colors.BLUE = "\033[94m"
        Colors.MAGENTA = "\033[95m"
        Colors.CYAN = "\033[96m"
        Colors.WHITE = "\033[97m"
        Colors.BOLD = "\033[1m"
        Colors.DIM = "\033[2m"
        Colors.UNDERLINE = "\033[4m"
        Colors.RESET = "\033[0m"

    def test_colors_defined(self):
        """All color codes should be defined."""
        assert Colors.RED != ""
        assert Colors.GREEN != ""
        assert Colors.YELLOW != ""
        assert Colors.BLUE != ""
        assert Colors.CYAN != ""
        assert Colors.RESET != ""

    def test_disable_colors(self):
        """Disabling colors should set all to empty strings."""
        Colors.disable()

        assert Colors.RED == ""
        assert Colors.GREEN == ""
        assert Colors.RESET == ""


class TestCreateJsonOutput:
    """Tests for JSON output creation."""

    def test_basic_json_output(self):
        """Basic JSON output should have correct structure."""
        results = [
            ScanResult(port=80, state="open", service="http"),
            ScanResult(port=443, state="open", service="https"),
            ScanResult(port=22, state="closed", service="ssh"),
        ]

        output = create_json_output(results, "192.168.1.1", 5.5)

        assert output["target"] == "192.168.1.1"
        assert output["duration_seconds"] == 5.5
        assert output["summary"]["total_ports"] == 3
        assert output["summary"]["open"] == 2
        assert output["summary"]["closed"] == 1
        assert len(output["results"]) == 3

    def test_json_result_fields(self):
        """Each result should have required fields."""
        results = [
            ScanResult(
                port=80,
                state="open",
                service="http",
                banner="Apache",
                response_time=0.025,
            )
        ]

        output = create_json_output(results, "test", 1.0)
        result = output["results"][0]

        assert result["port"] == 80
        assert result["state"] == "open"
        assert result["service"] == "http"
        assert result["banner"] == "Apache"
        assert result["response_time_ms"] == 25.0


class TestCreateCsvOutput:
    """Tests for CSV output creation."""

    def test_csv_header(self):
        """CSV should have correct header."""
        results = []
        output = create_csv_output(results)

        assert output == "port,state,service,banner,response_time_ms"

    def test_csv_data_rows(self):
        """CSV should contain data rows."""
        results = [
            ScanResult(port=80, state="open", service="http", banner="Test"),
        ]

        output = create_csv_output(results)
        lines = output.split("\n")

        assert len(lines) == 2
        assert "80,open,http" in lines[1]

    def test_csv_escapes_quotes(self):
        """Quotes in banner should be escaped."""
        results = [
            ScanResult(port=80, state="open", banner='Server: "Apache"'),
        ]

        output = create_csv_output(results)

        # Double quotes should be escaped
        assert '""Apache""' in output


class TestOutputFormatter:
    """Tests for OutputFormatter class."""

    def setup_method(self):
        """Reset colors before each test."""
        Colors.RED = "\033[91m"
        Colors.GREEN = "\033[92m"
        Colors.YELLOW = "\033[93m"
        Colors.BLUE = "\033[94m"
        Colors.MAGENTA = "\033[95m"
        Colors.CYAN = "\033[96m"
        Colors.WHITE = "\033[97m"
        Colors.BOLD = "\033[1m"
        Colors.DIM = "\033[2m"
        Colors.UNDERLINE = "\033[4m"
        Colors.RESET = "\033[0m"

    def test_formatter_initialization(self):
        """Formatter should initialize with options."""
        formatter = OutputFormatter(use_color=False, quiet=True)

        assert formatter.use_color is False
        assert formatter.quiet is True

    def test_formatter_quiet_mode(self):
        """Quiet mode should suppress non-essential output."""
        import io

        stream = io.StringIO()
        formatter = OutputFormatter(quiet=True, stream=stream)

        # These should not produce output in quiet mode
        formatter.print_header("test", 100, 10, 1.0)
        formatter.print_info("test info")
        formatter.print_warning("test warning")

        output = stream.getvalue()
        assert output == ""

    def test_formatter_print_header(self):
        """Header should print scan configuration."""
        import io

        stream = io.StringIO()
        formatter = OutputFormatter(use_color=False, quiet=False, stream=stream)
        formatter.print_header("192.168.1.1", 100, 50, 1.0, "TCP Connect")

        output = stream.getvalue()
        assert "192.168.1.1" in output
        assert "100" in output
        assert "50" in output

    def test_formatter_print_result_open(self):
        """Open port result should be printed."""
        import io

        stream = io.StringIO()
        formatter = OutputFormatter(use_color=False, quiet=False, stream=stream)
        result = ScanResult(port=80, state="open", service="http")
        formatter.print_result(result)

        output = stream.getvalue()
        assert "80" in output
        assert "OPEN" in output

    def test_formatter_print_result_closed_hidden(self):
        """Closed port should be hidden by default."""
        import io

        stream = io.StringIO()
        formatter = OutputFormatter(use_color=False, quiet=False, stream=stream)
        result = ScanResult(port=80, state="closed", service="http")
        formatter.print_result(result, show_closed=False)

        output = stream.getvalue()
        assert output == ""

    def test_formatter_print_result_closed_shown(self):
        """Closed port should be shown when requested."""
        import io

        stream = io.StringIO()
        formatter = OutputFormatter(use_color=False, quiet=False, stream=stream)
        result = ScanResult(port=80, state="closed", service="http")
        formatter.print_result(result, show_closed=True)

        output = stream.getvalue()
        assert "80" in output
        assert "CLOSED" in output

    def test_formatter_print_summary(self):
        """Summary should print statistics."""
        import io

        stream = io.StringIO()
        formatter = OutputFormatter(use_color=False, quiet=False, stream=stream)
        formatter.print_summary(
            total_ports=100,
            open_ports=5,
            filtered_ports=2,
            duration=1.5,
            hosts_scanned=1,
        )

        output = stream.getvalue()
        assert "100" in output
        assert "5" in output
        assert "COMPLETE" in output

    def test_formatter_print_progress(self):
        """Progress should be printable."""
        import io

        stream = io.StringIO()
        formatter = OutputFormatter(use_color=False, quiet=False, stream=stream)
        formatter.print_progress(50, 100, "192.168.1.1")

        output = stream.getvalue()
        assert "50" in output or "%" in output

    def test_formatter_verbose_mode(self):
        """Verbose mode should show debug messages."""
        import io

        stream = io.StringIO()
        formatter = OutputFormatter(
            use_color=False, quiet=False, verbose=True, stream=stream
        )
        formatter.print_debug("Debug message")

        output = stream.getvalue()
        assert "Debug" in output

    def test_formatter_print_host_header(self):
        """Host header should print for multi-host scans."""
        import io

        stream = io.StringIO()
        formatter = OutputFormatter(use_color=False, quiet=False, stream=stream)
        formatter.print_host_header("example.com", "93.184.216.34")

        output = stream.getvalue()
        assert "example.com" in output


class TestScanResultDataclass:
    """Tests for ScanResult dataclass."""

    def test_scan_result_creation(self):
        """ScanResult should be creatable with required fields."""
        result = ScanResult(port=80, state="open")

        assert result.port == 80
        assert result.state == "open"
        assert result.service == ""
        assert result.banner == ""
        assert result.response_time == 0.0

    def test_scan_result_all_fields(self):
        """ScanResult should accept all fields."""
        result = ScanResult(
            port=443,
            state="open",
            service="https",
            banner="nginx/1.18.0",
            response_time=0.015,
        )

        assert result.port == 443
        assert result.service == "https"
        assert result.banner == "nginx/1.18.0"
        assert result.response_time == 0.015
