from __future__ import annotations

import json
from pathlib import Path

import pytest

from pinconv2.errors import GateFailedError, InvalidTransitionError, StoreError
from pinconv2.fixtures.toffee_plan import build_plan
from pinconv2.fixtures.toffee_research import PROJECT_ID
from pinconv2.models import Project, ProjectState
from pinconv2.service import (
    build_gate_packet,
    init_project,
    run_approval,
    run_concept,
    run_critique,
    run_export,
    run_plan,
    run_previews,
    run_research,
    run_resolution,
    run_validation,
)
from pinconv2.store import ProjectStore


def _run_to_v1(store: ProjectStore) -> None:
    init_project(store)
    run_research(store)
    run_concept(store)
    run_plan(store)


def _run_to_gate(store: ProjectStore) -> None:
    _run_to_v1(store)
    run_validation(store)
    run_critique(store)
    run_resolution(store)
    report = run_validation(store)
    assert report.passed
    run_critique(store)
    build_gate_packet(store)


def test_out_of_order_command_is_rejected(store: ProjectStore) -> None:
    init_project(store)
    with pytest.raises(InvalidTransitionError):
        run_concept(store)


def test_validation_and_critique_bind_to_the_plan_hash(store: ProjectStore) -> None:
    _run_to_v1(store)
    validation = run_validation(store)
    critique = run_critique(store)
    plan = store.load_latest_plan(PROJECT_ID)
    assert validation.plan_hash == plan.plan_hash()
    assert critique.plan_hash == plan.plan_hash()
    assert not validation.passed
    assert critique.top3 == ["CF-01", "CF-02", "CF-03"]


def test_gate1_blocks_a_failing_revision(store: ProjectStore) -> None:
    _run_to_v1(store)
    run_validation(store)
    run_critique(store)
    with pytest.raises(GateFailedError):
        build_gate_packet(store)


def test_resolution_creates_revision_two_and_gate1_passes(store: ProjectStore) -> None:
    _run_to_gate(store)
    project = store.load_project(PROJECT_ID)
    assert project.state is ProjectState.GATE1_READY
    packet = store.load_packet(PROJECT_ID, 2)
    assert packet.validation_passed
    assert not packet.blockers
    assert packet.ready_shots == ["SH-01", "SH-02", "SH-03", "SH-04"]
    assert packet.conditions


def test_previews_are_available_before_approval(store: ProjectStore) -> None:
    _run_to_gate(store)
    paths = run_previews(store)
    assert len(paths) == 5
    assert all(path.is_file() for path in paths)


def test_approval_requires_gate1_ready(store: ProjectStore) -> None:
    _run_to_v1(store)
    with pytest.raises(InvalidTransitionError):
        run_approval(
            store,
            PROJECT_ID,
            approver="Test Reviewer",
            role="Test Role",
            evidence="pytest://not-reached",
        )


def test_export_requires_approval(store: ProjectStore) -> None:
    _run_to_gate(store)
    with pytest.raises(InvalidTransitionError):
        run_export(store)


def test_full_pipeline_with_synthetic_test_approval(store: ProjectStore) -> None:
    _run_to_gate(store)
    approval = run_approval(
        store,
        PROJECT_ID,
        approver="Pipeline Test Reviewer",
        role="Automated pipeline test",
        evidence="pytest://gate-1-pipeline-test",
        approved_exact_data=["ED-05", "ED-06", "ED-07"],
        note="Synthetic test fixture, not a production creative approval.",
    )
    plan = store.load_latest_plan(PROJECT_ID)
    assert approval.plan_hash == plan.plan_hash()
    project = store.load_project(PROJECT_ID)
    assert project.state is ProjectState.APPROVED

    paths = run_export(store)
    assert len(paths) == 13
    export_dir = store.export_dir(PROJECT_ID, 2)
    for name in [
        "concept-note.md",
        "production-plan.md",
        "gate1-packet.md",
        "level2-handoff.json",
        "production-plan.json",
        "concept-note.json",
        "research-pack.json",
        "brief.md",
        "previews/SH-01.svg",
        "previews/SH-02.svg",
        "previews/SH-03.svg",
        "previews/SH-04.svg",
        "previews/contact-sheet.svg",
    ]:
        assert (export_dir / name).is_file()
    handoff = json.loads((export_dir / "level2-handoff.json").read_text(encoding="utf-8"))
    assert handoff["plan_hash"] == plan.plan_hash()
    assert handoff["approval"]["approver"] == "Pipeline Test Reviewer"
    assert handoff["approval"]["bundle_hash"] == approval.bundle_hash
    assert handoff["exact_data_approved"] == ["ED-05", "ED-06", "ED-07"]
    assert handoff["exact_data_pending"] == []
    assert len(handoff["held_items"]) == 3
    assert len(handoff["shots"]) == 4
    events = store.list_events(PROJECT_ID)
    assert any(event["type"] == "gate1.approved" for event in events)
    assert any(event["type"] == "level1.exported" for event in events)


def test_approval_refuses_a_packet_bound_to_another_hash(store: ProjectStore) -> None:
    _run_to_gate(store)
    packet_path = store.project_dir(PROJECT_ID) / "gate" / "packet-rev-002.json"
    payload = json.loads(packet_path.read_text(encoding="utf-8"))
    payload["plan_hash"] = "0" * 64
    packet_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(GateFailedError):
        run_approval(
            store,
            PROJECT_ID,
            approver="Test Reviewer",
            role="Test Role",
            evidence="pytest://hash-mismatch",
        )


def test_store_refuses_a_different_plan_at_the_same_revision(store: ProjectStore) -> None:
    project = Project(id="store-test", title="Store test", state=ProjectState.INIT)
    store.create_project(project)
    plan = build_plan(project_id="store-test")
    store.save_plan(plan)
    store.save_plan(plan)
    changed = plan.model_copy(update={"assumptions": ["different assumption"]})
    with pytest.raises(StoreError):
        store.save_plan(changed)


def test_revision_two_has_a_different_hash(plan_v1, plan_v2) -> None:
    assert plan_v1.revision == 1
    assert plan_v2.revision == 2
    assert plan_v1.plan_hash() != plan_v2.plan_hash()


def test_resolution_report_is_persisted(store: ProjectStore) -> None:
    _run_to_gate(store)
    resolution = store.load_resolution(PROJECT_ID, 2)
    assert resolution.from_revision == 1
    assert resolution.to_revision == 2
    assert [item.critique_finding_id for item in resolution.inputs] == [
        "CF-01",
        "CF-02",
        "CF-03",
    ]
    assert [item.status.value for item in resolution.inputs] == [
        "resolved",
        "escalated",
        "resolved",
    ]


def test_gate_packet_lists_bundle_holds_and_exact_data(store: ProjectStore) -> None:
    _run_to_gate(store)
    packet = store.load_packet(PROJECT_ID, 2)
    assert packet.bundle.bundle_hash
    assert set(packet.bundle.record_hashes) == {
        "brief",
        "research",
        "concept",
        "plan",
        "validation",
        "critique",
        "resolution",
    }
    assert [item.id for item in packet.held_items] == ["HI-01", "HI-02", "HI-03"]
    assert packet.exact_data_pending == ["ED-05", "ED-06", "ED-07"]
    assert packet.exact_data_approved == []


def test_resolution_records_verified_impacts(store: ProjectStore) -> None:
    _run_to_gate(store)
    resolution = store.load_resolution(PROJECT_ID, 2)
    assert set(resolution.verified_impacts) == {"CF-01", "CF-02", "CF-03"}
    assert all(changes for changes in resolution.verified_impacts.values())
    assert set(resolution.applied_fixes) == {
        "safe_area",
        "commercial",
        "budget",
        "fallback",
        "rights",
    }


def test_automation_cannot_record_approval(store: ProjectStore) -> None:
    _run_to_gate(store)
    with pytest.raises(GateFailedError):
        run_approval(
            store,
            PROJECT_ID,
            approver="Agent",
            role="Automation",
            evidence="agent://self",
            actor_kind="agent",
        )


def test_approval_scope_must_be_ready(store: ProjectStore) -> None:
    _run_to_gate(store)
    packet = store.load_packet(PROJECT_ID, 2)
    store.save_packet(packet.model_copy(update={"ready_shots": ["SH-01"]}))
    with pytest.raises(GateFailedError):
        run_approval(
            store,
            PROJECT_ID,
            approver="Test Reviewer",
            role="Test Role",
            evidence="pytest://scope-test",
            scope=["SH-04"],
        )


def test_changed_concept_blocks_approval(store: ProjectStore) -> None:
    _run_to_gate(store)
    concept = store.load_concept(PROJECT_ID)
    store.save_concept(
        concept.model_copy(update={"audience_summary": "Changed after the packet."})
    )
    with pytest.raises(GateFailedError):
        run_approval(
            store,
            PROJECT_ID,
            approver="Test Reviewer",
            role="Test Role",
            evidence="pytest://changed-concept",
        )


def test_changed_concept_blocks_export(store: ProjectStore) -> None:
    _run_to_gate(store)
    run_approval(
        store,
        PROJECT_ID,
        approver="Test Reviewer",
        role="Test Role",
        evidence="pytest://export-bundle-test",
    )
    concept = store.load_concept(PROJECT_ID)
    store.save_concept(
        concept.model_copy(update={"audience_summary": "Changed after approval."})
    )
    with pytest.raises(GateFailedError):
        run_export(store)


def test_unapproved_exact_data_stays_pending(store: ProjectStore) -> None:
    _run_to_gate(store)
    run_approval(
        store,
        PROJECT_ID,
        approver="Test Reviewer",
        role="Test Role",
        evidence="pytest://exact-pending-test",
    )
    run_export(store)
    handoff = json.loads(
        (store.export_dir(PROJECT_ID, 2) / "level2-handoff.json").read_text(
            encoding="utf-8"
        )
    )
    assert handoff["exact_data_approved"] == []
    assert handoff["exact_data_pending"] == ["ED-05", "ED-06", "ED-07"]


def test_partial_approval_filters_audio_assets(store: ProjectStore) -> None:
    _run_to_gate(store)
    run_approval(
        store,
        PROJECT_ID,
        approver="Test Reviewer",
        role="Test Role",
        evidence="pytest://partial-scope-test",
        scope=["SH-04"],
        approved_exact_data=["ED-05", "ED-06", "ED-07"],
    )
    run_export(store)
    handoff = json.loads(
        (store.export_dir(PROJECT_ID, 2) / "level2-handoff.json").read_text(
            encoding="utf-8"
        )
    )
    assert [shot["shot_id"] for shot in handoff["shots"]] == ["SH-04"]
    asset_ids = {asset["asset_id"] for asset in handoff["assets"]}
    assert "AS-11" in asset_ids
    assert "AS-09" not in asset_ids
    assert "AS-10" not in asset_ids


def test_validation_is_idempotent(store: ProjectStore) -> None:
    _run_to_v1(store)
    first = run_validation(store)
    events_before = len(store.list_events(PROJECT_ID))
    second = run_validation(store)
    assert first.created_at == second.created_at
    assert len(store.list_events(PROJECT_ID)) == events_before


def test_path_escape_is_rejected(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    with pytest.raises(StoreError):
        store.load_project("..\\outside")


def test_export_paths_are_inside_the_project(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    _run_to_gate(store)
    run_approval(
        store,
        PROJECT_ID,
        approver="Test Reviewer",
        role="Test Role",
        evidence="pytest://export-path-test",
    )
    for path in run_export(store):
        assert path.is_relative_to(store.project_dir(PROJECT_ID))
