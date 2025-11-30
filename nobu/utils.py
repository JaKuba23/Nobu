"""
Utility functions for parsing targets, ports, and common operations.
"""

import ipaddress
import socket
from typing import List, Set

__all__ = [
    "parse_ports",
    "parse_target",
    "resolve_hostname",
    "get_service_name",
    "format_duration",
    "validate_timeout",
    "validate_threads",
    "is_private_ip",
]

# Common ports used in predefined scan profiles
COMMON_PORTS: dict[str, List[int]] = {
    "top20": [
        21,
        22,
        23,
        25,
        53,
        80,
        110,
        111,
        135,
        139,
        143,
        443,
        445,
        993,
        995,
        1723,
        3306,
        3389,
        5900,
        8080,
    ],
    "top100": [
        7,
        9,
        13,
        21,
        22,
        23,
        25,
        26,
        37,
        53,
        79,
        80,
        81,
        88,
        106,
        110,
        111,
        113,
        119,
        135,
        139,
        143,
        144,
        179,
        199,
        389,
        427,
        443,
        444,
        445,
        465,
        513,
        514,
        515,
        543,
        544,
        548,
        554,
        587,
        631,
        646,
        873,
        990,
        993,
        995,
        1025,
        1026,
        1027,
        1028,
        1029,
        1110,
        1433,
        1720,
        1723,
        1755,
        1900,
        2000,
        2001,
        2049,
        2121,
        2717,
        3000,
        3128,
        3306,
        3389,
        3986,
        4899,
        5000,
        5009,
        5051,
        5060,
        5101,
        5190,
        5357,
        5432,
        5631,
        5666,
        5800,
        5900,
        6000,
        6001,
        6646,
        7070,
        8000,
        8008,
        8009,
        8080,
        8081,
        8443,
        8888,
        9100,
        9999,
        10000,
        32768,
        49152,
        49153,
        49154,
    ],
    "web": [
        80,
        443,
        8000,
        8008,
        8080,
        8443,
        8888,
        3000,
        3001,
        4000,
        5000,
        5001,
        9000,
        9090,
        9443,
    ],
    "database": [
        1433,
        1521,
        3306,
        5432,
        6379,
        9042,
        27017,
        28017,
        5984,
        7474,
        8529,
        9200,
        9300,
        11211,
        26257,
    ],
    "mail": [25, 110, 143, 465, 587, 993, 995, 2525],
    "full": list(range(1, 1025)),  # Standard well-known ports
}


def parse_ports(port_spec: str) -> List[int]:
    """
    Parse port specification string into a list of port numbers.

    Supports formats:
        - Single port: "80"
        - Port range: "1-1024"
        - Port list: "22,80,443"
        - Mixed: "22,80-90,443,8080-8090"

    Args:
        port_spec: Port specification string

    Returns:
        Sorted list of unique port numbers

    Raises:
        ValueError: If port specification is invalid
    """
    if not port_spec or not port_spec.strip():
        raise ValueError("Port specification cannot be empty")

    ports: Set[int] = set()

    parts = port_spec.replace(" ", "").split(",")

    for part in parts:
        if not part:
            continue

        if "-" in part:
            range_parts = part.split("-")
            if len(range_parts) != 2:
                raise ValueError(f"Invalid port range: {part}")

            try:
                start = int(range_parts[0])
                end = int(range_parts[1])
            except ValueError as e:
                raise ValueError(f"Invalid port numbers in range: {part}") from e

            if start > end:
                raise ValueError(f"Invalid range: start ({start}) > end ({end})")

            if start < 1 or end > 65535:
                raise ValueError("Port numbers must be between 1 and 65535")

            ports.update(range(start, end + 1))
        else:
            try:
                port = int(part)
            except ValueError as e:
                raise ValueError(f"Invalid port number: {part}") from e

            if port < 1 or port > 65535:
                raise ValueError(f"Port {port} out of valid range (1-65535)")

            ports.add(port)

    if not ports:
        raise ValueError("No valid ports specified")

    return sorted(ports)


def parse_target(target: str) -> List[str]:
    """
    Parse target specification into a list of IP addresses or hostnames.

    Supports:
        - Single IP: "192.168.1.1"
        - CIDR notation: "192.168.1.0/24"
        - Hostname: "scanme.nmap.org"

    Args:
        target: Target specification string

    Returns:
        List of IP addresses or hostnames to scan

    Raises:
        ValueError: If target specification is invalid
    """
    if not target or not target.strip():
        raise ValueError("Target cannot be empty")

    target = target.strip()

    # Check if it's a CIDR notation
    if "/" in target:
        try:
            network = ipaddress.ip_network(target, strict=False)
            # Limit to /16 networks to prevent accidental massive scans
            if network.num_addresses > 65536:
                raise ValueError(
                    f"Network {target} is too large ({network.num_addresses} hosts). "
                    "Maximum allowed is /16 (65536 hosts)."
                )
            return [str(ip) for ip in network.hosts()]
        except ValueError as e:
            raise ValueError(f"Invalid CIDR notation: {target}. {e}")

    # Try to parse as single IP
    try:
        ip = ipaddress.ip_address(target)
        return [str(ip)]
    except ValueError:
        pass

    # Treat as hostname - validate by attempting resolution
    try:
        socket.gethostbyname(target)
        return [target]
    except socket.gaierror:
        raise ValueError(f"Cannot resolve hostname: {target}")


def resolve_hostname(host: str) -> str:
    """
    Resolve hostname to IP address.

    Args:
        host: Hostname or IP address

    Returns:
        IP address as string

    Raises:
        ValueError: If hostname cannot be resolved
    """
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        raise ValueError(f"Cannot resolve hostname: {host}")


def get_service_name(port: int, protocol: str = "tcp") -> str:
    """
    Get the common service name for a port number.

    Args:
        port: Port number
        protocol: Protocol (tcp/udp)

    Returns:
        Service name or empty string if unknown
    """
    try:
        return socket.getservbyport(port, protocol)
    except (OSError, socket.error):
        return ""


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def validate_timeout(timeout: float) -> float:
    """
    Validate and normalize timeout value.

    Args:
        timeout: Timeout in seconds

    Returns:
        Validated timeout value

    Raises:
        ValueError: If timeout is invalid
    """
    if timeout <= 0:
        raise ValueError("Timeout must be a positive number")
    if timeout > 30:
        raise ValueError("Timeout cannot exceed 30 seconds")
    return timeout


def validate_threads(threads: int) -> int:
    """
    Validate and normalize thread count.

    Args:
        threads: Number of threads

    Returns:
        Validated thread count

    Raises:
        ValueError: If thread count is invalid
    """
    if threads < 1:
        raise ValueError("Thread count must be at least 1")
    if threads > 1000:
        raise ValueError("Thread count cannot exceed 1000")
    return threads


def is_private_ip(ip: str) -> bool:
    """
    Check if an IP address is in a private range.

    Args:
        ip: IP address string

    Returns:
        True if IP is private, False otherwise
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False
