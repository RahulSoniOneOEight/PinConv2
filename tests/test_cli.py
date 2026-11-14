from __future__ import annotations

import json
from pathlib import Path

from pinconv2.cli import main


def test_cli_run_all_approve_and_export(tmp_path: Path, capsys) -> None:
    data_dir = str(tmp_path / "cli-projects")
    assert main(["--data-dir", data_dir, "run-all"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["state"] == "gate1_ready"
    assert status["validation"]["passed"] is True
    assert status["gate1"]["blockers"] == []

    assert (
        main(
            [
                "--data-dir",
                data_dir,
                "approve",
                "--reviewer",
                "CLI Test Reviewer",
                "--role",
                "Automated CLI test",
                "--evidence",
                "pytest://cli-test",
                "--confirm",
                "APPROVE",
                "--approve-exact-data",
                "all",
            ]
        )
        == 0
    )
    approval = json.loads(capsys.readouterr().out)
    assert approval["approved"] is True

    assert main(["--data-dir", data_dir, "export"]) == 0
    paths = json.loads(capsys.readouterr().out)
    assert len(paths) == 13
    assert all(Path(path).is_file() for path in paths)


def test_cli_validate_returns_failure_for_revision_one(tmp_path: Path, capsys) -> None:
    data_dir = str(tmp_path / "cli-projects")
    for command in ["init", "research", "concept", "plan"]:
        assert main(["--data-dir", data_dir, command]) == 0
    capsys.readouterr()
    assert main(["--data-dir", data_dir, "validate"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["passed"] is False
    assert payload["failures"]


def test_cli_status_reports_missing_gate(tmp_path: Path, capsys) -> None:
    data_dir = str(tmp_path / "cli-projects")
    assert main(["--data-dir", data_dir, "init"]) == 0
    capsys.readouterr()
    assert main(["--data-dir", data_dir, "status"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["state"] == "intake"
    assert status["plan_revision"] == 0
