"""
Entry point for running Nobu as a module.

Usage:
    python -m nobu scan --target 192.168.1.1 --ports 1-1024
    python -m nobu profile fast --target scanme.nmap.org
"""

import sys
from nobu.cli import main

if __name__ == "__main__":
    sys.exit(main())
