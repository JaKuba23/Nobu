# Nobu

```
 ███╗   ██╗ ██████╗ ██████╗ ██╗   ██╗
 ████╗  ██║██╔═══██╗██╔══██╗██║   ██║
 ██╔██╗ ██║██║   ██║██████╔╝██║   ██║
 ██║╚██╗██║██║   ██║██╔══██╗██║   ██║
 ██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝
 ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝ 
```

**Lightweight CLI port scanner for network reconnaissance and learning.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/JaKuba23/nobu/actions/workflows/ci.yml/badge.svg)](https://github.com/JaKuba23/nobu/actions)

---

## Motivation

I built Nobu to deepen my understanding of network fundamentals while improving my Python skills. Working through concepts like TCP handshakes, socket programming, and concurrent execution helped me bridge the gap between theoretical knowledge and practical implementation.

The project is named after a character from Ghost of Tsushima - a subtle nod to the stealth and reconnaissance themes that align with network scanning concepts.

**Important:** This tool is designed for educational purposes and authorized testing only. Never scan networks or systems without explicit permission from the owner.

---

## Features

- **TCP Connect Scanning** — Full TCP handshake for reliable port detection
- **CIDR Range Support** — Scan entire subnets with `/24`, `/16` notation
- **Multithreaded Engine** — Configurable thread pool (1-1000 threads)
- **Banner Grabbing** — Extract service information from open ports
- **Predefined Profiles** — Quick access to common scan configurations
- **Colored Output** — ANSI colors for easy result interpretation
- **JSON/CSV Export** — Save results for further analysis
- **Progress Tracking** — Real-time progress bar during scans
- **Zero Dependencies** — Uses only Python standard library

---

## Installation

### Requirements

- Python 3.10 or higher
- Unix-like system (Linux, macOS) or Windows

### From Source

```bash
# Clone the repository
git clone https://github.com/JaKuba23/nobu.git
cd nobu

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Verify installation
nobu --version
```

### Development Setup

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or use requirements file
pip install -r requirements-dev.txt
```

---

## Usage

### Basic Scan

Scan common ports on a single host:

```bash
nobu scan --target 192.168.1.1 --ports 1-1024
```

### Using Profiles

Profiles provide predefined configurations for common scenarios:

```bash
# Fast scan - top 100 ports
nobu profile fast --target 192.168.1.1

# Web server ports
nobu profile web --target example.com

# Database ports
nobu profile database --target db.internal

# Full scan - ports 1-1024
nobu profile full --target 10.0.0.5
```

Available profiles:

| Profile | Ports | Description |
|---------|-------|-------------|
| `fast` | Top 100 | Quick reconnaissance scan |
| `full` | 1-1024 | All well-known ports |
| `web` | 15 ports | HTTP, HTTPS, common frameworks |
| `database` | 15 ports | MySQL, PostgreSQL, MongoDB, Redis |
| `mail` | 8 ports | SMTP, POP3, IMAP |
| `stealth` | Top 20 | Slow, low-profile scan |

### Subnet Scanning

Scan entire network ranges using CIDR notation:

```bash
# Scan a /24 subnet
nobu scan --target 192.168.1.0/24 --ports 22,80,443

# Scan specific ports across a network
nobu scan --target 10.0.0.0/24 --ports 3389 --threads 200
```

### Banner Grabbing

Attempt to retrieve service banners from open ports:

```bash
nobu scan --target 192.168.1.1 --ports 20-100 --banner
```

### Export Results

Save scan results to JSON or CSV:

```bash
# JSON output
nobu scan --target 192.168.1.1 --ports 1-1024 --output results.json

# CSV output
nobu profile fast --target example.com --output scan.csv
```

### Additional Options

```bash
# Adjust timeout (seconds)
nobu scan --target slow-host.local --ports 80,443 --timeout 3.0

# Increase thread count for faster scans
nobu scan --target 192.168.1.1 --ports 1-65535 --threads 500

# Disable colored output (for piping/logging)
nobu scan --target 192.168.1.1 --ports 80 --no-color

# Quiet mode - only show open ports
nobu scan --target 192.168.1.1 --ports 1-1024 --quiet

# Verbose mode - show debug info
nobu scan --target 192.168.1.1 --ports 80 --verbose
```

### Command Reference

```
nobu <command> [options]

Commands:
  scan      Perform a custom port scan
  profile   Run a predefined scan profile

Global Options:
  --version     Show version information
  --no-color    Disable colored output
  --help        Show help message
```

---

## How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Layer                                │
│  ┌─────────┐    ┌──────────────┐    ┌─────────────────────┐     │
│  │ argparse│───▶│ NobuCLI      │───▶│ Profile/Scan Config │     │
│  └─────────┘    └──────────────┘    └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Scanner Engine                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐     │
│  │ ThreadPoolExec. │───▶│ Worker Threads (scan_port)      │     │
│  │ (concurrent.    │    │ ┌────────┐ ┌────────┐ ┌────────┐│     │
│  │  futures)       │    │ │Socket 1│ │Socket 2│ │Socket N││     │
│  └─────────────────┘    │ └────────┘ └────────┘ └────────┘│     │
│                         └─────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Output Layer                               │
│  ┌─────────────────┐    ┌──────────────┐    ┌───────────────┐   │
│  │ OutputFormatter │───▶│ ANSI Colors  │───▶│ JSON/CSV      │   │
│  │ (aligned text)  │    │ (optional)   │    │ (optional)    │   │
│  └─────────────────┘    └──────────────┘    └───────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Scanning Process

1. **Target Resolution**: Hostnames are resolved to IP addresses. CIDR ranges are expanded into individual host lists.

2. **Thread Pool Creation**: A `ThreadPoolExecutor` is initialized with the specified number of worker threads.

3. **Port Scanning**: Each port scan creates a TCP socket and attempts a `connect()`. The result determines the port state:
   - **Connection successful** → Port is `OPEN`
   - **Connection refused** → Port is `CLOSED`
   - **Timeout/No response** → Port is `FILTERED`

4. **Banner Grabbing** (optional): For open ports, the scanner attempts to receive data or sends a basic HTTP probe to extract service information.

5. **Result Aggregation**: Results are collected, sorted by port number, and formatted for display.

### Technical Details

The scanner uses **TCP Connect scanning**, which performs a complete three-way handshake:

```
Client          Server
  │    SYN       │
  │─────────────▶│
  │   SYN-ACK    │
  │◀─────────────│
  │    ACK       │
  │─────────────▶│
  │  (connected) │
```

This approach is reliable but not stealthy - it leaves connection logs on target systems. For professional penetration testing, tools like Nmap with SYN scanning provide better options.

**Performance Considerations:**

- Default thread count (100) balances speed and resource usage
- Higher thread counts improve speed but may trigger rate limiting
- Socket timeouts affect scan duration on filtered/slow hosts
- CIDR ranges > /16 are blocked to prevent accidental large-scale scans

---

## Project Structure

```
nobu/
├── nobu/
│   ├── __init__.py     # Package metadata, ASCII banner
│   ├── __main__.py     # Module entry point
│   ├── cli.py          # Argument parsing, command dispatch
│   ├── scanner.py      # Core scanning engine
│   ├── output.py       # Formatting, colors, export
│   └── utils.py        # Port/target parsing, helpers
├── tests/
│   ├── test_utils.py   # Utility function tests
│   ├── test_scanner.py # Scanner logic tests
│   └── test_output.py  # Output formatting tests
├── examples/
│   └── commands.md     # Example command reference
├── .github/
│   └── workflows/
│       └── ci.yml      # GitHub Actions CI
├── pyproject.toml      # Project configuration
├── requirements-dev.txt
├── LICENSE
├── README.md
└── README_PL.md        # Polish documentation
```

---

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=nobu --cov-report=term-missing

# Specific test file
pytest tests/test_utils.py -v
```

---

## Docker Test Lab

The project includes a Docker Compose environment for safe, legal testing. It creates isolated containers with various services to scan.

### Quick Start

```bash
cd docker-lab
docker-compose up -d

# Scan the lab
nobu profile lab --target 127.0.0.1 --banner
```

### Available Services

| Service     | Port(s)     | Description                  |
|-------------|-------------|------------------------------|
| Nginx       | 8080, 8443  | Web server (HTTP/HTTPS)      |
| Apache      | 8081        | Alternative web server       |
| SSH         | 2222        | OpenSSH server               |
| MySQL       | 3306        | MySQL 8.0 database           |
| PostgreSQL  | 5432        | PostgreSQL 15 database       |
| Redis       | 6379        | Redis cache                  |
| MongoDB     | 27017       | MongoDB 6 database           |
| MailHog     | 1025, 8025  | SMTP test server + Web UI    |
| FTP         | 21          | vsftpd FTP server            |

See [docker-lab/README.md](docker-lab/README.md) for detailed documentation.

---

## Limitations & Ethics

### Technical Limitations

- **TCP only** — No UDP scanning (planned for future release)
- **No OS fingerprinting** — Detects open ports, not operating systems
- **Connect scanning** — Creates full connections, visible in target logs
- **No evasion techniques** — Rate limiting and IDS may block scans

### Ethical Guidelines

This tool is intended for:

- Learning network fundamentals
- Scanning your own lab environments
- Authorized penetration testing with written permission
- Network troubleshooting on systems you manage

This tool is **NOT** intended for:

- Scanning networks without authorization
- Bypassing security controls
- Any malicious or illegal activity

**Always obtain written permission before scanning any network or system you don't own.** Unauthorized port scanning may violate laws in your jurisdiction (CFAA in the US, Computer Misuse Act in the UK, etc.).

For production security assessments, use established tools like Nmap, Masscan, or commercial solutions, and follow your organization's security policies.

---

## Roadmap

Planned features for future releases:

- [ ] **UDP Scanning** — Detect UDP services (DNS, SNMP, etc.)
- [ ] **Service Fingerprinting** — Identify service versions using probe database
- [ ] **XML/HTML Reports** — Generate formatted scan reports
- [ ] **Configuration Files** — Save and load scan configurations
- [ ] **Ping Sweep** — Host discovery before port scanning
- [ ] **Rate Limiting Controls** — Fine-grained control over scan speed
- [ ] **Plugin System** — Extensible architecture for custom checks
- [ ] **Web Interface** — Simple dashboard for scan management

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- The socket programming techniques are inspired by classic network security resources
- Profile port selections are based on common service configurations
- Project structure follows Python packaging best practices

---

**Note:** "Nobu is a subtle reference to the Ghost of Tsushima"

