"""
Nobu - Lightweight CLI Port Scanner

A fast, multithreaded port scanner built with Python standard library.
Designed for learning network fundamentals and lab environments.
"""

__version__ = "0.1.0"
__author__ = "JaKuba23"

BANNER = r"""
 ███╗   ██╗ ██████╗ ██████╗ ██╗   ██╗
 ████╗  ██║██╔═══██╗██╔══██╗██║   ██║
 ██╔██╗ ██║██║   ██║██████╔╝██║   ██║
 ██║╚██╗██║██║   ██║██╔══██╗██║   ██║
 ██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝
 ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝
        ~ Port Scanner v{version} ~
"""


def get_banner(colorize: bool = True) -> str:
    """Return the ASCII banner with optional ANSI coloring."""
    from nobu.output import Colors

    banner = BANNER.format(version=__version__)

    if colorize:
        lines = banner.split("\n")
        colored_lines = []
        for line in lines:
            if "~" in line:
                colored_lines.append(f"{Colors.CYAN}{line}{Colors.RESET}")
            elif "█" in line or "╗" in line or "╚" in line:
                colored_lines.append(f"{Colors.RED}{line}{Colors.RESET}")
            else:
                colored_lines.append(line)
        return "\n".join(colored_lines)

    return banner
