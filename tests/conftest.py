from __future__ import annotations

from pathlib import Path

import pytest

from pinconv2.fixtures.toffee_plan import build_plan, revision_two_applied
from pinconv2.fixtures.toffee_research import build_brief
from pinconv2.store import ProjectStore


@pytest.fixture()
def brief():
    return build_brief()


@pytest.fixture()
def plan_v1():
    return build_plan()


@pytest.fixture()
def plan_v2():
    return build_plan(revision=2, applied=revision_two_applied())


@pytest.fixture()
def store(tmp_path: Path) -> ProjectStore:
    return ProjectStore(tmp_path / "projects")
