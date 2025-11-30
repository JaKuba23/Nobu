# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- UDP scanning support
- Service fingerprinting
- XML/HTML report generation
- Configuration file support
- Ping sweep for host discovery

---

## [0.1.0] - 2024-12-01

### Added
- Initial release of Nobu port scanner
- TCP connect scanning engine with multithreading
- CIDR range support for subnet scanning
- Banner grabbing for open ports
- Six predefined scan profiles:
  - `fast` - Top 100 common ports
  - `full` - All well-known ports (1-1024)
  - `web` - Web server ports
  - `database` - Database ports
  - `mail` - Email server ports
  - `stealth` - Slow, low-profile scan
- Colored terminal output with ANSI codes
- JSON and CSV export functionality
- Progress bar for scan tracking
- Quiet and verbose modes
- Comprehensive CLI with help text
- Unit tests for core functionality
- GitHub Actions CI pipeline

### Technical Details
- Built with Python standard library only
- Thread pool implementation using `concurrent.futures`
- Socket-based TCP connection testing
- Configurable timeout and thread count
- Support for Python 3.10, 3.11, and 3.12

---

## Version History

- **0.1.0** - Initial release with core scanning functionality

[Unreleased]: https://github.com/JaKuba23/nobu/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/JaKuba23/nobu/releases/tag/v0.1.0

