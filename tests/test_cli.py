"""Tests for CLI entry point."""

from __future__ import annotations

import pytest

from paperfinder.cli import main


class TestCLI:
    def test_version(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit, match="0"):
            main(["--version"])
        captured = capsys.readouterr()
        assert "0.1.0" in captured.out

    def test_no_command_exits(self) -> None:
        with pytest.raises(SystemExit, match="1"):
            main([])
