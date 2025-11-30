"""
Core scanning engine with multithreaded TCP connect scanning.
"""

import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, Iterator, List, Optional

__all__ = [
    "ScanConfig",
    "ScanStats",
    "ScanResult",
    "PortScanner",
    "quick_scan",
]

from nobu.output import ScanResult
from nobu.utils import get_service_name, resolve_hostname


@dataclass
class ScanConfig:
    """Configuration for a scan operation."""

    targets: List[str]
    ports: List[int]
    threads: int = 100
    timeout: float = 1.0
    banner_grab: bool = False
    show_closed: bool = False

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.targets:
            raise ValueError("At least one target is required")
        if not self.ports:
            raise ValueError("At least one port is required")
        if self.threads < 1:
            raise ValueError("Thread count must be at least 1")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")


@dataclass
class ScanStats:
    """Statistics for a completed scan."""

    total_ports: int = 0
    open_ports: int = 0
    closed_ports: int = 0
    filtered_ports: int = 0
    hosts_scanned: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0

    @property
    def duration(self) -> float:
        """Get scan duration in seconds."""
        return self.end_time - self.start_time

    def update(self, result: ScanResult) -> None:
        """Update statistics with a new result."""
        self.total_ports += 1
        if result.state == "open":
            self.open_ports += 1
        elif result.state == "closed":
            self.closed_ports += 1
        else:
            self.filtered_ports += 1


class PortScanner:
    """
    Multithreaded TCP connect port scanner.

    Uses a thread pool to scan multiple ports concurrently.
    Supports banner grabbing for open ports.
    """

    BANNER_PROBE = b"HEAD / HTTP/1.0\r\n\r\n"
    BANNER_RECV_SIZE = 1024
    BANNER_TIMEOUT = 2.0

    def __init__(self, config: ScanConfig):
        """
        Initialize the scanner with configuration.

        Args:
            config: Scan configuration
        """
        self.config = config
        self.stats = ScanStats()
        self._stop_flag = False

    def __repr__(self) -> str:
        """Return string representation of scanner configuration."""
        return (
            f"PortScanner(targets={len(self.config.targets)}, "
            f"ports={len(self.config.ports)}, "
            f"threads={self.config.threads}, "
            f"timeout={self.config.timeout}s)"
        )

    def stop(self) -> None:
        """Signal the scanner to stop."""
        self._stop_flag = True

    def scan_port(self, host: str, port: int) -> ScanResult:
        """
        Scan a single port on a host.

        Args:
            host: Target hostname or IP
            port: Port number to scan

        Returns:
            ScanResult with port state and optional banner
        """
        # Validate port range
        if not (1 <= port <= 65535):
            raise ValueError(f"Port {port} out of valid range (1-65535)")

        result = ScanResult(port=port, state="closed", service=get_service_name(port))

        start_time = time.time()

        try:
            # Resolve hostname to IP for consistent connection
            ip = resolve_hostname(host)

            # Create socket and attempt connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.config.timeout)

            try:
                connection_result = sock.connect_ex((ip, port))
                result.response_time = time.time() - start_time

                if connection_result == 0:
                    result.state = "open"

                    # Attempt banner grab if enabled
                    if self.config.banner_grab:
                        result.banner = self._grab_banner(sock)
            finally:
                sock.close()

        except socket.timeout:
            result.state = "filtered"
            result.response_time = time.time() - start_time

        except socket.gaierror:
            # DNS resolution failed
            result.state = "filtered"

        except OSError as e:
            # Connection refused or other OS-level error
            if e.errno == 111:  # Connection refused
                result.state = "closed"
            else:
                result.state = "filtered"

        return result

    def _grab_banner(self, sock: socket.socket) -> str:
        """
        Attempt to grab service banner from open socket.

        Args:
            sock: Connected socket

        Returns:
            Banner string or empty string
        """
        # Store original socket timeout
        original_timeout = sock.gettimeout()
        try:
            sock.settimeout(self.BANNER_TIMEOUT)

            # Try to receive without sending first (some services send banner)
            try:
                banner = sock.recv(self.BANNER_RECV_SIZE)
                if banner:
                    return self._decode_banner(banner)
            except BlockingIOError:
                pass

            # Send HTTP probe for web services
            try:
                sock.send(self.BANNER_PROBE)
                banner = sock.recv(self.BANNER_RECV_SIZE)
                return self._decode_banner(banner)
            except (socket.error, OSError):
                pass

        except (socket.timeout, socket.error, OSError):
            pass
        finally:
            # Restore original timeout
            sock.settimeout(original_timeout)

        return ""

    def _decode_banner(self, data: bytes) -> str:
        """
        Decode banner bytes to string safely.

        Args:
            data: Raw banner bytes

        Returns:
            Cleaned banner string
        """
        try:
            # Try UTF-8 first
            banner = data.decode("utf-8", errors="ignore")
        except UnicodeDecodeError:
            # Fall back to latin-1
            banner = data.decode("latin-1", errors="ignore")

        # Clean up the banner
        banner = banner.strip()
        # Remove null bytes and control characters
        banner = "".join(c if c.isprintable() or c in "\t " else "" for c in banner)
        # Take first line only
        banner = banner.split("\n")[0].strip()
        # Limit length
        return banner[:100]

    def scan_host(
        self,
        host: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Iterator[ScanResult]:
        """
        Scan all configured ports on a single host.

        Args:
            host: Target hostname or IP
            progress_callback: Optional callback(current, total, host)

        Yields:
            ScanResult for each port
        """
        total = len(self.config.ports)
        completed = 0

        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            # Submit all port scans
            future_to_port = {
                executor.submit(self.scan_port, host, port): port
                for port in self.config.ports
            }

            # Process results as they complete
            for future in as_completed(future_to_port):
                if self._stop_flag:
                    executor.shutdown(wait=False, cancel_futures=True)
                    return

                completed += 1

                if progress_callback:
                    progress_callback(completed, total, host)

                try:
                    result = future.result()
                    self.stats.update(result)
                    yield result
                except Exception:
                    # Log error but continue scanning
                    port = future_to_port[future]
                    yield ScanResult(port=port, state="filtered")

    def scan_all(
        self,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        host_callback: Optional[Callable[[str, str], None]] = None,
    ) -> Iterator[tuple[str, List[ScanResult]]]:
        """
        Scan all configured targets.

        Args:
            progress_callback: Optional callback(current, total, host)
            host_callback: Optional callback(host, ip) when starting new host

        Yields:
            Tuple of (host, list of results) for each target
        """
        self.stats = ScanStats()
        self.stats.start_time = time.time()

        for host in self.config.targets:
            if self._stop_flag:
                break

            self.stats.hosts_scanned += 1

            # Resolve and notify
            try:
                ip = resolve_hostname(host)
                if host_callback:
                    host_callback(host, ip)
            except ValueError:
                if host_callback:
                    host_callback(host, "")
                continue

            # Collect results for this host
            results = list(self.scan_host(host, progress_callback))

            # Sort by port number
            results.sort(key=lambda r: r.port)

            yield (host, results)

        self.stats.end_time = time.time()


def quick_scan(
    host: str, ports: List[int], timeout: float = 1.0, threads: int = 50
) -> List[ScanResult]:
    """
    Convenience function for quick port scan.

    Args:
        host: Target hostname or IP
        ports: List of ports to scan
        timeout: Socket timeout in seconds
        threads: Number of worker threads

    Returns:
        List of scan results, sorted by port
    """
    config = ScanConfig(targets=[host], ports=ports, threads=threads, timeout=timeout)

    scanner = PortScanner(config)
    results = list(scanner.scan_host(host))
    results.sort(key=lambda r: r.port)

    return results
