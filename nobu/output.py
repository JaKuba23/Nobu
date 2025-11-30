"""
Output formatting and terminal color handling.
"""

import sys
from dataclasses import dataclass
from typing import TextIO

__all__ = [
    "Colors",
    "ScanResult",
    "OutputFormatter",
    "create_json_output",
    "create_csv_output",
]


class Colors:
    """ANSI color codes for terminal output."""

    # Basic colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # Reset
    RESET = "\033[0m"

    @classmethod
    def disable(cls) -> None:
        """Disable all colors by setting them to empty strings."""
        cls.RED = ""
        cls.GREEN = ""
        cls.YELLOW = ""
        cls.BLUE = ""
        cls.MAGENTA = ""
        cls.CYAN = ""
        cls.WHITE = ""
        cls.BOLD = ""
        cls.DIM = ""
        cls.UNDERLINE = ""
        cls.RESET = ""


def supports_color() -> bool:
    """
    Check if the terminal supports ANSI colors.

    Returns:
        True if terminal supports colors, False otherwise
    """
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False

    # Check for common environment indicators
    import os

    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False

    return True


@dataclass
class ScanResult:
    """Container for individual port scan result."""

    port: int
    state: str  # "open", "closed", "filtered"
    service: str = ""
    banner: str = ""
    response_time: float = 0.0


class OutputFormatter:
    """
    Handles all output formatting for the scanner.

    Provides consistent, aligned output that looks clean
    in a standard 80-column terminal.
    """

    COLUMN_WIDTH = 80
    PORT_COL = 8
    STATE_COL = 12
    SERVICE_COL = 15

    def __init__(
        self,
        use_color: bool = True,
        quiet: bool = False,
        verbose: bool = False,
        stream: TextIO = sys.stdout,
    ):
        """
        Initialize the output formatter.

        Args:
            use_color: Enable ANSI color output
            quiet: Quiet mode - only show open ports
            verbose: Verbose mode - show debug information
            stream: Output stream (default: stdout)
        """
        self.use_color = use_color and supports_color()
        self.quiet = quiet
        self.verbose = verbose
        self.stream = stream

        if not self.use_color:
            Colors.disable()

    def print(self, message: str = "", end: str = "\n") -> None:
        """Print message to output stream."""
        print(message, end=end, file=self.stream)

    def print_banner(self, banner: str) -> None:
        """Print the application banner."""
        if not self.quiet:
            self.print(banner)

    def print_header(
        self,
        target: str,
        ports_count: int,
        threads: int,
        timeout: float,
        mode: str = "TCP Connect",
    ) -> None:
        """
        Print scan header with configuration details.

        Args:
            target: Target specification
            ports_count: Number of ports to scan
            threads: Number of threads
            timeout: Socket timeout
            mode: Scan mode description
        """
        if self.quiet:
            return

        self.print(f"{Colors.BOLD}{'═' * self.COLUMN_WIDTH}{Colors.RESET}")
        self.print(f"{Colors.CYAN}Target:{Colors.RESET}    {target}")
        self.print(f"{Colors.CYAN}Ports:{Colors.RESET}     {ports_count}")
        self.print(f"{Colors.CYAN}Threads:{Colors.RESET}   {threads}")
        self.print(f"{Colors.CYAN}Timeout:{Colors.RESET}   {timeout}s")
        self.print(f"{Colors.CYAN}Mode:{Colors.RESET}      {mode}")
        self.print(f"{Colors.BOLD}{'═' * self.COLUMN_WIDTH}{Colors.RESET}")
        self.print()

        # Column headers
        header = (
            f"{'PORT':<{self.PORT_COL}}"
            f"{'STATE':<{self.STATE_COL}}"
            f"{'SERVICE':<{self.SERVICE_COL}}"
            f"BANNER/INFO"
        )
        self.print(f"{Colors.BOLD}{header}{Colors.RESET}")
        self.print(f"{Colors.DIM}{'-' * self.COLUMN_WIDTH}{Colors.RESET}")

    def print_result(self, result: ScanResult, show_closed: bool = False) -> None:
        """
        Print a single port scan result.

        Args:
            result: Scan result to display
            show_closed: Whether to show closed ports
        """
        if result.state == "closed" and (self.quiet or not show_closed):
            return

        # Color based on state
        if result.state == "open":
            state_color = Colors.GREEN
            state_display = "OPEN"
        elif result.state == "filtered":
            state_color = Colors.YELLOW
            state_display = "FILTERED"
        else:
            state_color = Colors.RED
            state_display = "CLOSED"

        # Format port with service
        port_str = f"{result.port}/tcp"
        service_str = result.service if result.service else "-"

        # Truncate banner if too long
        banner_max = (
            self.COLUMN_WIDTH - self.PORT_COL - self.STATE_COL - self.SERVICE_COL - 4
        )
        banner_str = result.banner[:banner_max] if result.banner else ""
        if len(result.banner) > banner_max:
            banner_str = banner_str[:-3] + "..."

        line = (
            f"{port_str:<{self.PORT_COL}}"
            f"{state_color}{state_display:<{self.STATE_COL}}{Colors.RESET}"
            f"{service_str:<{self.SERVICE_COL}}"
            f"{Colors.DIM}{banner_str}{Colors.RESET}"
        )

        self.print(line)

    def print_progress(self, current: int, total: int, host: str = "") -> None:
        """
        Print progress indicator.

        Args:
            current: Current progress count
            total: Total count
            host: Current host being scanned
        """
        if self.quiet:
            return

        percentage = (current / total) * 100
        bar_width = 30
        filled = int(bar_width * current / total)
        bar = "█" * filled + "░" * (bar_width - filled)

        host_info = f" [{host}]" if host else ""
        progress_line = (
            f"\r{Colors.CYAN}Progress:{Colors.RESET} [{bar}] "
            f"{percentage:5.1f}% ({current}/{total}){host_info}"
        )

        # Pad to clear previous line
        self.print(f"{progress_line:<{self.COLUMN_WIDTH}}", end="")
        self.stream.flush()

    def clear_progress(self) -> None:
        """Clear the progress line."""
        self.print(f"\r{' ' * self.COLUMN_WIDTH}\r", end="")

    def print_host_header(self, host: str, ip: str = "") -> None:
        """
        Print header for a new host in multi-host scan.

        Args:
            host: Hostname or IP
            ip: Resolved IP (if different from host)
        """
        if self.quiet:
            return

        self.print()
        ip_info = f" ({ip})" if ip and ip != host else ""
        self.print(
            f"{Colors.BOLD}{Colors.MAGENTA}▶ Scanning: {host}{ip_info}{Colors.RESET}"
        )
        self.print(f"{Colors.DIM}{'-' * 40}{Colors.RESET}")

    def print_summary(
        self,
        total_ports: int,
        open_ports: int,
        filtered_ports: int,
        duration: float,
        hosts_scanned: int = 1,
    ) -> None:
        """
        Print scan summary.

        Args:
            total_ports: Total ports scanned
            open_ports: Number of open ports found
            filtered_ports: Number of filtered ports
            duration: Scan duration in seconds
            hosts_scanned: Number of hosts scanned
        """
        from nobu.utils import format_duration

        self.print()
        self.print(f"{Colors.BOLD}{'═' * self.COLUMN_WIDTH}{Colors.RESET}")
        self.print(f"{Colors.BOLD}SCAN COMPLETE{Colors.RESET}")
        self.print(f"{Colors.DIM}{'-' * 40}{Colors.RESET}")

        if hosts_scanned > 1:
            self.print(f"  Hosts scanned:    {hosts_scanned}")

        self.print(f"  Ports scanned:    {total_ports}")
        self.print(f"  {Colors.GREEN}Open ports:{Colors.RESET}       {open_ports}")

        if filtered_ports > 0:
            self.print(
                f"  {Colors.YELLOW}Filtered ports:{Colors.RESET}   {filtered_ports}"
            )

        self.print(f"  Scan duration:    {format_duration(duration)}")
        self.print(f"{Colors.BOLD}{'═' * self.COLUMN_WIDTH}{Colors.RESET}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        error_msg = f"{Colors.RED}[ERROR]{Colors.RESET} {message}"
        # Error messages always go to stderr regardless of stream setting
        print(error_msg, file=sys.stderr)

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        if not self.quiet:
            self.print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {message}")

    def print_info(self, message: str) -> None:
        """Print info message."""
        if not self.quiet:
            self.print(f"{Colors.CYAN}[INFO]{Colors.RESET} {message}")

    def print_debug(self, message: str) -> None:
        """Print debug message (only in verbose mode)."""
        if self.verbose:
            self.print(f"{Colors.DIM}[DEBUG] {message}{Colors.RESET}")


def create_json_output(results: list[ScanResult], target: str, duration: float) -> dict:
    """
    Create JSON-serializable output from scan results.

    Args:
        results: List of scan results
        target: Target specification
        duration: Scan duration

    Returns:
        Dictionary ready for JSON serialization
    """
    return {
        "target": target,
        "duration_seconds": round(duration, 3),
        "summary": {
            "total_ports": len(results),
            "open": sum(1 for r in results if r.state == "open"),
            "closed": sum(1 for r in results if r.state == "closed"),
            "filtered": sum(1 for r in results if r.state == "filtered"),
        },
        "results": [
            {
                "port": r.port,
                "state": r.state,
                "service": r.service,
                "banner": r.banner,
                "response_time_ms": round(r.response_time * 1000, 2),
            }
            for r in results
        ],
    }


def create_csv_output(results: list[ScanResult]) -> str:
    """
    Create CSV output from scan results.

    Args:
        results: List of scan results

    Returns:
        CSV formatted string
    """
    lines = ["port,state,service,banner,response_time_ms"]

    for r in results:
        # Escape quotes in banner
        banner = r.banner.replace('"', '""')
        lines.append(
            f'{r.port},{r.state},{r.service},"{banner}",'
            f"{round(r.response_time * 1000, 2)}"
        )

    return "\n".join(lines)
