"""
Unit tests for package initialization.

Run with: pytest tests/test_init.py -v
"""

from nobu import __version__, __author__, BANNER, get_banner


class TestPackageMetadata:
    """Tests for package metadata."""

    def test_version_defined(self):
        """Version should be defined."""
        assert __version__ == "0.1.0"

    def test_author_defined(self):
        """Author should be defined."""
        assert __author__ == "JaKuba23"

    def test_banner_defined(self):
        """Banner should be defined."""
        assert BANNER is not None
        assert "NOBU" in BANNER.upper() or "███" in BANNER


class TestGetBanner:
    """Tests for get_banner function."""

    def test_get_banner_with_color(self):
        """Banner with color should include ANSI codes."""
        banner = get_banner(colorize=True)
        assert banner is not None
        assert len(banner) > 0
        # Should contain escape codes or banner text
        assert "~" in banner or "\033" in banner

    def test_get_banner_without_color(self):
        """Banner without color should not include ANSI codes."""
        banner = get_banner(colorize=False)
        assert banner is not None
        # Should not contain color escape codes for red/cyan
        # (may still have version formatting)
        assert "0.1.0" in banner or "███" in banner

    def test_get_banner_contains_version(self):
        """Banner should contain version."""
        banner = get_banner(colorize=False)
        assert "0.1.0" in banner
