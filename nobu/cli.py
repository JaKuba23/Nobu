"""
Command-line interface for Nobu port scanner.

Provides a Cisco-style CLI experience with subcommands and rich help.
"""

import argparse
import json
import signal
import sys
import time
from types import FrameType
from typing import Dict, List, Optional, TypedDict

__all__ = [
    "ProfileConfig",
    "PROFILES",
    "NobuCLI",
    "main",
]

from nobu import __version__, get_banner
from nobu.output import (
    OutputFormatter,
    ScanResult,
    create_csv_output,
    create_json_output,
)
from nobu.scanner import PortScanner, ScanConfig
from nobu.utils import COMMON_PORTS, parse_ports, parse_target


class ProfileConfig(TypedDict):
    """Type definition for scan profile configuration."""

    description: str
    ports: List[int]
    threads: int
    timeout: float


# Scan profiles with predefined configurations
PROFILES: Dict[str, ProfileConfig] = {
    "fast": {
        "description": "Quick scan of top 100 common ports",
        "ports": COMMON_PORTS["top100"],
        "threads": 200,
        "timeout": 0.5,
    },
    "full": {
        "description": "Comprehensive scan of well-known ports (1-1024)",
        "ports": COMMON_PORTS["full"],
        "threads": 150,
        "timeout": 1.0,
    },
    "web": {
        "description": "Web server ports (HTTP, HTTPS, common frameworks)",
        "ports": COMMON_PORTS["web"],
        "threads": 50,
        "timeout": 1.0,
    },
    "database": {
        "description": "Common database ports (MySQL, PostgreSQL, MongoDB, etc.)",
        "ports": COMMON_PORTS["database"],
        "threads": 30,
        "timeout": 2.0,
    },
    "mail": {
        "description": "Email server ports (SMTP, POP3, IMAP)",
        "ports": COMMON_PORTS["mail"],
        "threads": 20,
        "timeout": 2.0,
    },
    "stealth": {
        "description": "Slow, low-profile scan (fewer threads, longer timeout)",
        "ports": COMMON_PORTS["top20"],
        "threads": 5,
        "timeout": 3.0,
    },
    "lab": {
        "description": "Docker test lab ports (web, db, ssh, mail)",
        "ports": [21, 1025, 2222, 3306, 5432, 6379, 8025, 8080, 8081, 8443, 27017],
        "threads": 20,
        "timeout": 2.0,
    },
}


class NobuCLI:
    """
    Main CLI handler for Nobu port scanner.

    Handles argument parsing, command dispatch, and output coordination.
    """

    def __init__(self) -> None:
        """Initialize the CLI handler."""
        self.parser = self._create_parser()
        self.formatter: Optional[OutputFormatter] = None
        self.scanner: Optional[PortScanner] = None
        self._interrupted = False

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all subcommands."""
        # Main parser
        parser = argparse.ArgumentParser(
            prog="nobu",
            description="Nobu - Lightweight CLI Port Scanner",
            epilog="""
Examples:
  nobu scan --target 192.168.1.1 --ports 1-1024
  nobu scan --target 10.0.0.0/24 --ports 22,80,443 --threads 200
  nobu profile fast --target scanme.nmap.org
  nobu profile web --target example.com --banner

For more information, visit: https://github.com/JaKuba23/nobu
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument(
            "--version",
            action="store_true",
            help="Show version information and exit",
        )

        parser.add_argument(
            "--no-color",
            action="store_true",
            help="Disable colored terminal output",
        )

        # Subcommands
        subparsers = parser.add_subparsers(
            dest="command",
            title="Commands",
            description="Available scan modes",
            metavar="<command>",
        )

        # Scan subcommand
        scan_parser = subparsers.add_parser(
            "scan",
            help="Perform a custom port scan",
            description="Scan specified ports on target host(s)",
            epilog="""
Examples:
  nobu scan --target 192.168.1.1 --ports 80,443
  nobu scan --target 10.0.0.0/24 --ports 1-1024 --threads 200
  nobu scan --target example.com --ports 22,80,443 --banner --timeout 2
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self._add_scan_arguments(scan_parser)

        # Profile subcommand
        profile_parser = subparsers.add_parser(
            "profile",
            help="Run a predefined scan profile",
            description="Execute a predefined scan configuration",
            epilog=f"""
Available profiles:
{self._format_profiles()}

Examples:
  nobu profile fast --target 192.168.1.1
  nobu profile web --target example.com --banner
  nobu profile database --target db.internal.local
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self._add_profile_arguments(profile_parser)

        return parser

    def _add_scan_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add arguments for the scan subcommand."""
        parser.add_argument(
            "-t",
            "--target",
            required=True,
            help="Target IP, hostname, or CIDR range (e.g., 192.168.1.0/24)",
        )

        parser.add_argument(
            "-p",
            "--ports",
            default="1-1024",
            help="Ports to scan: range, list, or mixed (default: 1-1024)",
        )

        parser.add_argument(
            "-T",
            "--threads",
            type=int,
            default=100,
            help="Number of concurrent threads (default: 100, max: 1000)",
        )

        parser.add_argument(
            "--timeout",
            type=float,
            default=1.0,
            help="Socket timeout in seconds (default: 1.0)",
        )

        parser.add_argument(
            "-b",
            "--banner",
            action="store_true",
            help="Attempt to grab service banners from open ports",
        )

        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="Quiet mode: only show open ports",
        )

        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Verbose mode: show detailed progress",
        )

        parser.add_argument(
            "-o",
            "--output",
            help="Save results to file (supports .json and .csv)",
        )

        parser.add_argument(
            "--no-color",
            action="store_true",
            help="Disable colored output",
        )

        parser.add_argument(
            "--show-closed",
            action="store_true",
            help="Show closed ports in output",
        )

    def _add_profile_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add arguments for the profile subcommand."""
        parser.add_argument(
            "profile",
            choices=list(PROFILES.keys()),
            help="Scan profile to use",
        )

        parser.add_argument(
            "-t",
            "--target",
            required=True,
            help="Target IP, hostname, or CIDR range",
        )

        parser.add_argument(
            "-b",
            "--banner",
            action="store_true",
            help="Attempt to grab service banners",
        )

        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="Quiet mode: only show open ports",
        )

        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Verbose mode: show detailed progress",
        )

        parser.add_argument(
            "-o",
            "--output",
            help="Save results to file (supports .json and .csv)",
        )

        parser.add_argument(
            "--no-color",
            action="store_true",
            help="Disable colored output",
        )

    def _format_profiles(self) -> str:
        """Format available profiles for help text."""
        lines = []
        for name, config in PROFILES.items():
            port_count = len(config["ports"])
            lines.append(f"  {name:12} {config['description']} ({port_count} ports)")
        return "\n".join(lines)

    def _handle_interrupt(
        self, signum: Optional[int], frame: Optional[FrameType]
    ) -> None:
        """Handle keyboard interrupt gracefully."""
        self._interrupted = True
        if self.scanner:
            self.scanner.stop()
        if self.formatter:
            self.formatter.clear_progress()
            self.formatter.print()
            self.formatter.print_warning("Scan interrupted by user")

    def run(self, args: Optional[list] = None) -> int:
        """
        Run the CLI with given arguments.

        Args:
            args: Command line arguments (default: sys.argv)

        Returns:
            Exit code (0 for success, non-zero for errors)
        """
        # Set up interrupt handler
        signal.signal(signal.SIGINT, self._handle_interrupt)

        parsed = self.parser.parse_args(args)

        # Handle --version at top level
        if parsed.version:
            self._print_version()
            return 0

        # Initialize formatter with color setting
        use_color = not getattr(parsed, "no_color", False)
        quiet = getattr(parsed, "quiet", False)
        verbose = getattr(parsed, "verbose", False)

        self.formatter = OutputFormatter(
            use_color=use_color,
            quiet=quiet,
            verbose=verbose,
        )

        # Dispatch to command handler
        if parsed.command == "scan":
            return self._run_scan(parsed)
        elif parsed.command == "profile":
            return self._run_profile(parsed)
        else:
            # No command specified - show help with banner
            print(get_banner(use_color))
            self.parser.print_help()
            return 0

    def _print_version(self) -> None:
        """Print version information with easter egg."""
        print(
            f"""
{get_banner(True)}

Version:  {__version__}
Python:   {sys.version.split()[0]}
Platform: {sys.platform}

"Nobu is a subtle reference to the Ghost of Tsushima"
        """
        )

    def _run_scan(self, args: argparse.Namespace) -> int:
        """Execute the scan command."""
        assert self.formatter is not None
        try:
            # Parse targets and ports
            targets = parse_target(args.target)
            ports = parse_ports(args.ports)

            # Validate parameters
            threads = min(max(args.threads, 1), 1000)
            timeout = max(args.timeout, 0.1)

            # Create scan configuration
            config = ScanConfig(
                targets=targets,
                ports=ports,
                threads=threads,
                timeout=timeout,
                banner_grab=args.banner,
                show_closed=getattr(args, "show_closed", False),
            )

            return self._execute_scan(config, args)

        except ValueError as e:
            self.formatter.print_error(str(e))
            return 1
        except Exception as e:
            self.formatter.print_error(f"Unexpected error: {e}")
            if getattr(args, "verbose", False):
                import traceback

                traceback.print_exc()
            return 1

    def _run_profile(self, args: argparse.Namespace) -> int:
        """Execute a predefined scan profile."""
        assert self.formatter is not None
        try:
            profile = PROFILES[args.profile]
            targets = parse_target(args.target)

            ports: List[int] = profile["ports"]
            threads: int = profile["threads"]
            timeout: float = profile["timeout"]

            config = ScanConfig(
                targets=targets,
                ports=ports,
                threads=threads,
                timeout=timeout,
                banner_grab=args.banner,
            )

            self.formatter.print_info(
                f"Using profile '{args.profile}': {profile['description']}"
            )

            return self._execute_scan(config, args)

        except ValueError as e:
            self.formatter.print_error(str(e))
            return 1

    def _execute_scan(self, config: ScanConfig, args: argparse.Namespace) -> int:
        """
        Execute the actual scan with given configuration.

        Args:
            config: Scan configuration
            args: Parsed command line arguments

        Returns:
            Exit code
        """
        assert self.formatter is not None

        # Print banner unless quiet
        if not args.quiet:
            print(get_banner(not getattr(args, "no_color", False)))

        # Print header
        self.formatter.print_header(
            target=args.target,
            ports_count=len(config.ports),
            threads=config.threads,
            timeout=config.timeout,
            mode="TCP Connect" + (" + Banner" if config.banner_grab else ""),
        )

        # Create scanner
        self.scanner = PortScanner(config)

        # Collect all results for output file
        all_results: list[ScanResult] = []

        # Capture formatter reference for callbacks
        formatter = self.formatter

        # Progress callback
        def on_progress(current: int, total: int, host: str) -> None:
            if not args.quiet:
                formatter.print_progress(current, total, host)

        # Host callback
        def on_host(host: str, ip: str) -> None:
            formatter.clear_progress()
            if len(config.targets) > 1:
                formatter.print_host_header(host, ip)

        # Execute scan
        start_time = time.time()

        try:
            for host, results in self.scanner.scan_all(on_progress, on_host):
                formatter.clear_progress()

                # Print results for this host
                for result in results:
                    all_results.append(result)
                    formatter.print_result(result, config.show_closed)

                if self._interrupted:
                    break

        except KeyboardInterrupt:
            self._handle_interrupt(None, None)

        # Calculate duration
        duration = time.time() - start_time

        # Print summary
        stats = self.scanner.stats
        formatter.print_summary(
            total_ports=stats.total_ports,
            open_ports=stats.open_ports,
            filtered_ports=stats.filtered_ports,
            duration=duration,
            hosts_scanned=stats.hosts_scanned,
        )

        # Save output file if requested
        if hasattr(args, "output") and args.output:
            self._save_output(args.output, all_results, args.target, duration)

        return 0 if not self._interrupted else 130

    def _save_output(
        self, filename: str, results: list[ScanResult], target: str, duration: float
    ) -> None:
        """Save results to output file."""
        assert self.formatter is not None
        try:
            if filename.endswith(".json"):
                data = create_json_output(results, target, duration)
                with open(filename, "w") as f:
                    json.dump(data, f, indent=2)
            elif filename.endswith(".csv"):
                csv_data = create_csv_output(results)
                with open(filename, "w") as f:
                    f.write(csv_data)
            else:
                # Default to JSON
                data = create_json_output(results, target, duration)
                with open(filename, "w") as f:
                    json.dump(data, f, indent=2)

            self.formatter.print_info(f"Results saved to: {filename}")

        except IOError as e:
            self.formatter.print_error(f"Failed to save output: {e}")


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Command line arguments (default: sys.argv)

    Returns:
        Exit code
    """
    cli = NobuCLI()
    return cli.run(args)


if __name__ == "__main__":
    sys.exit(main())
