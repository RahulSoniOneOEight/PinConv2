from __future__ import annotations

from pinconv2.critique import build_resolution_inputs, critique_plan
from pinconv2.validators import validate_plan


def test_top_three_are_safe_area_commercial_and_budget(plan_v1, brief) -> None:
    report = critique_plan(plan_v1, brief, validate_plan(plan_v1, brief))
    categories = {finding.id: finding.category for finding in report.findings}
    assert [categories[finding_id] for finding_id in report.top3] == [
        "safe_area",
        "commercial_data",
        "budget",
    ]


def test_findings_are_ranked_by_priority(plan_v1, brief) -> None:
    report = critique_plan(plan_v1, brief, validate_plan(plan_v1, brief))
    priorities = [finding.priority for finding in report.findings]
    assert priorities == sorted(priorities, reverse=True)
    assert all(finding.impact >= 1 for finding in report.findings)


def test_resolution_modes_match_the_finding(plan_v1, brief) -> None:
    report = critique_plan(plan_v1, brief, validate_plan(plan_v1, brief))
    actions = build_resolution_inputs(report)
    modes = {action["finding_id"]: action["mode"] for action in actions}
    assert modes["CF-01"] == "auto"
    assert modes["CF-02"] == "human"
    assert modes["CF-03"] == "auto"


def test_v2_has_no_material_findings(plan_v2, brief) -> None:
    report = critique_plan(plan_v2, brief, validate_plan(plan_v2, brief))
    assert report.findings == []
    assert report.top3 == []
    assert "No material findings" in report.summary
