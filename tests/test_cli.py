from __future__ import annotations

import argparse

import pytest
from onsetto_client import cli


def test_main_returns_130_on_keyboard_interrupt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def interrupt(_: argparse.Namespace) -> int:
        raise KeyboardInterrupt

    monkeypatch.setattr(cli, "update_account", interrupt)

    assert cli.main(["update-account"]) == 130


def test_update_account_returns_2_for_missing_configuration(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing_settings() -> object:
        raise ValueError("ONSETTO_EMAIL is required")

    monkeypatch.setattr("onsetto_client.cli.Settings.from_env", missing_settings)
    parser = cli.build_parser()
    args = parser.parse_args(["update-account"])

    result = cli.update_account(args)

    assert result == 2
    assert "ONSETTO_EMAIL is required" in caplog.text
