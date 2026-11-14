"""Folder-based, auditable project storage.

Layout for one project::

    projects/<project_id>/
      project.json
      brief.json
      research.json
      concept.json
      plans/rev-001.json
      validation/rev-001.json
      critique/rev-001.json
      resolutions/001-to-002.json
      gate/packet-rev-002.json
      approvals/rev-002.json
      exports/rev-002/...
      events.jsonl

Plans are immutable per revision: writing a different plan to an existing
revision is refused rather than silently changing an approved hash.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from .errors import NotFoundError, StoreError
from .models import (
    BriefRevision,
    ConceptNote,
    CritiqueReport,
    Gate1Approval,
    Gate1Packet,
    ProductionPlan,
    Project,
    ProjectState,
    ResearchPack,
    ResolutionReport,
    ValidationReport,
    utc_now,
)

T = TypeVar("T", bound=BaseModel)

_PLAN_PATTERN = re.compile(r"^rev-(\d{3})\.json$")


class ProjectStore:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    # -- paths ------------------------------------------------------------

    def project_dir(self, project_id: str) -> Path:
        return self._path(project_id)

    def _path(self, project_id: str, *parts: str) -> Path:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,60}", project_id):
            raise StoreError(f"invalid project id: {project_id!r}")
        target = (self.root / project_id).joinpath(*parts).resolve()
        if not target.is_relative_to(self.root):
            raise StoreError(f"path escapes the data root: {project_id!r}")
        return target

    @staticmethod
    def _rev(revision: int) -> str:
        return f"rev-{revision:03d}.json"

    # -- primitives -------------------------------------------------------

    def _write_text(self, path: Path, text: str, *, overwrite: bool = True) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not overwrite:
            raise StoreError(f"refusing to overwrite {path}")
        temporary = path.with_name(path.name + ".tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        temporary.replace(path)

    def _write_model(
        self, path: Path, model: BaseModel, *, overwrite: bool = True
    ) -> None:
        self._write_text(path, model.model_dump_json(indent=2) + "\n", overwrite=overwrite)

    def _read_model(self, path: Path, model_type: type[T]) -> T:
        if not path.is_file():
            raise NotFoundError(f"record not found: {path}")
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))

    # -- project ----------------------------------------------------------

    def create_project(self, project: Project) -> Project:
        path = self._path(project.id, "project.json")
        if path.exists():
            raise StoreError(f"project already exists: {project.id}")
        self._write_model(path, project, overwrite=False)
        self.append_event(
            project.id,
            "project.created",
            {"title": project.title, "state": project.state.value},
        )
        return project

    def load_project(self, project_id: str) -> Project:
        return self._read_model(self._path(project_id, "project.json"), Project)

    def save_project(self, project: Project) -> Project:
        self._write_model(self._path(project.id, "project.json"), project)
        return project

    def update_state(
        self, project_id: str, state: ProjectState, *, detail: dict[str, Any] | None = None
    ) -> Project:
        project = self.load_project(project_id)
        updated = project.model_copy(update={"state": state, "updated_at": utc_now()})
        self.save_project(updated)
        self.append_event(
            project_id,
            "project.state",
            {"from": project.state.value, "to": state.value, **(detail or {})},
        )
        return updated

    def set_plan_revision(self, project_id: str, revision: int) -> Project:
        project = self.load_project(project_id)
        updated = project.model_copy(
            update={"current_plan_revision": revision, "updated_at": utc_now()}
        )
        self.save_project(updated)
        return updated

    # -- brief, research, concept ----------------------------------------

    def save_brief(self, brief: BriefRevision) -> None:
        self._write_model(self._path(brief.project_id, "brief.json"), brief)
        self.append_event(
            brief.project_id,
            "brief.recorded",
            {"revision": brief.revision, "must_have": len(brief.must_have)},
        )

    def load_brief(self, project_id: str) -> BriefRevision:
        return self._read_model(self._path(project_id, "brief.json"), BriefRevision)

    def save_research(self, pack: ResearchPack) -> None:
        self._write_model(self._path(pack.project_id, "research.json"), pack)
        self.append_event(
            pack.project_id,
            "research.recorded",
            {"sources": len(pack.sources), "findings": len(pack.findings)},
        )

    def load_research(self, project_id: str) -> ResearchPack:
        return self._read_model(self._path(project_id, "research.json"), ResearchPack)

    def save_concept(self, concept: ConceptNote) -> None:
        self._write_model(self._path(concept.project_id, "concept.json"), concept)
        self.append_event(
            concept.project_id,
            "concept.recorded",
            {"revision": concept.revision, "recommended": concept.recommended_option_id},
        )

    def load_concept(self, project_id: str) -> ConceptNote:
        return self._read_model(self._path(project_id, "concept.json"), ConceptNote)

    # -- plans ------------------------------------------------------------

    def save_plan(self, plan: ProductionPlan) -> None:
        path = self._path(plan.project_id, "plans", self._rev(plan.revision))
        if path.exists():
            existing = self.load_plan(plan.project_id, plan.revision)
            if existing.plan_hash() != plan.plan_hash():
                raise StoreError(
                    f"plan revision {plan.revision} already exists with a different hash; "
                    "create a new revision instead"
                )
            return
        self._write_model(path, plan, overwrite=False)
        self.append_event(
            plan.project_id,
            "plan.recorded",
            {
                "revision": plan.revision,
                "hash": plan.plan_hash(),
                "shots": len(plan.shots),
                "layers": len(plan.layers),
                "assets": len(plan.assets),
            },
        )

    def load_plan(self, project_id: str, revision: int) -> ProductionPlan:
        return self._read_model(
            self._path(project_id, "plans", self._rev(revision)), ProductionPlan
        )

    def latest_plan_revision(self, project_id: str) -> int:
        directory = self._path(project_id, "plans")
        if not directory.is_dir():
            return 0
        revisions = [
            int(match.group(1))
            for path in directory.iterdir()
            if (match := _PLAN_PATTERN.match(path.name))
        ]
        return max(revisions, default=0)

    def load_latest_plan(self, project_id: str) -> ProductionPlan:
        revision = self.latest_plan_revision(project_id)
        if revision == 0:
            raise NotFoundError(f"no plan for project: {project_id}")
        return self.load_plan(project_id, revision)

    # -- validation and critique -----------------------------------------

    def save_validation(self, report: ValidationReport) -> None:
        path = self._path(
            report.project_id, "validation", self._rev(report.plan_revision)
        )
        if path.exists():
            existing = self.load_validation(report.project_id, report.plan_revision)
            if existing.model_dump(exclude={"created_at"}) == report.model_dump(
                exclude={"created_at"}
            ):
                return
            raise StoreError(
                f"validation for revision {report.plan_revision} already exists "
                "with different content"
            )
        self._write_model(path, report)
        self.append_event(
            report.project_id,
            "plan.validated",
            {
                "revision": report.plan_revision,
                "passed": report.passed,
                "failures": len(report.failures),
                "warnings": len(report.warnings),
            },
        )

    def load_validation(self, project_id: str, revision: int) -> ValidationReport:
        return self._read_model(
            self._path(project_id, "validation", self._rev(revision)), ValidationReport
        )

    def save_critique(self, report: CritiqueReport) -> None:
        path = self._path(
            report.project_id, "critique", self._rev(report.plan_revision)
        )
        if path.exists():
            existing = self.load_critique(report.project_id, report.plan_revision)
            if existing.model_dump(exclude={"created_at"}) == report.model_dump(
                exclude={"created_at"}
            ):
                return
            raise StoreError(
                f"critique for revision {report.plan_revision} already exists "
                "with different content"
            )
        self._write_model(path, report)
        self.append_event(
            report.project_id,
            "plan.critiqued",
            {
                "revision": report.plan_revision,
                "findings": len(report.findings),
                "top3": report.top3,
            },
        )

    def load_critique(self, project_id: str, revision: int) -> CritiqueReport:
        return self._read_model(
            self._path(project_id, "critique", self._rev(revision)), CritiqueReport
        )

    # -- resolutions, gate and approval ----------------------------------

    def save_resolution(self, report: ResolutionReport) -> None:
        name = f"{report.from_revision:03d}-to-{report.to_revision:03d}.json"
        path = self._path(report.project_id, "resolutions", name)
        if path.exists():
            existing = self._read_model(path, ResolutionReport)
            if existing.model_dump(exclude={"created_at"}) == report.model_dump(
                exclude={"created_at"}
            ):
                return
            raise StoreError(f"resolution already exists with different content: {name}")
        self._write_model(path, report)
        self.append_event(
            report.project_id,
            "inputs.updated",
            {
                "from": report.from_revision,
                "to": report.to_revision,
                "inputs": len(report.inputs),
            },
        )

    def load_resolution(self, project_id: str, to_revision: int) -> ResolutionReport:
        directory = self._path(project_id, "resolutions")
        if not directory.is_dir():
            raise NotFoundError(f"no resolutions for project: {project_id}")
        for path in sorted(directory.iterdir()):
            if not path.name.endswith(f"-to-{to_revision:03d}.json"):
                continue
            return self._read_model(path, ResolutionReport)
        raise NotFoundError(f"no resolution to revision {to_revision}")

    def latest_resolution(self, project_id: str) -> ResolutionReport | None:
        directory = self._path(project_id, "resolutions")
        if not directory.is_dir():
            return None
        paths = sorted(directory.glob("*.json"))
        if not paths:
            return None
        return self._read_model(paths[-1], ResolutionReport)

    def save_packet(self, packet: Gate1Packet) -> None:
        self._write_model(
            self._path(packet.project_id, "gate", f"packet-rev-{packet.plan_revision:03d}.json"),
            packet,
        )
        self.append_event(
            packet.project_id,
            "gate1.packet",
            {
                "revision": packet.plan_revision,
                "validation_passed": packet.validation_passed,
                "blockers": len(packet.blockers),
            },
        )

    def load_packet(self, project_id: str, revision: int) -> Gate1Packet:
        return self._read_model(
            self._path(project_id, "gate", f"packet-rev-{revision:03d}.json"), Gate1Packet
        )

    def save_approval(self, approval: Gate1Approval) -> None:
        path = self._path(
            approval.project_id, "approvals", self._rev(approval.plan_revision)
        )
        if path.exists():
            raise StoreError(
                f"an approval already exists for revision {approval.plan_revision}"
            )
        self._write_model(path, approval)
        self.append_event(
            approval.project_id,
            "gate1.approved",
            {
                "revision": approval.plan_revision,
                "hash": approval.plan_hash,
                "approver": approval.approver,
                "scope": approval.scope,
            },
        )

    def load_approval(self, project_id: str, revision: int) -> Gate1Approval:
        return self._read_model(
            self._path(project_id, "approvals", self._rev(revision)), Gate1Approval
        )

    # -- exports and events ----------------------------------------------

    def export_dir(self, project_id: str, revision: int) -> Path:
        return self._path(project_id, "exports", f"rev-{revision:03d}")

    def write_export(self, project_id: str, revision: int, name: str, text: str) -> Path:
        path = self.export_dir(project_id, revision) / name
        self._write_text(path, text)
        return path

    def append_event(self, project_id: str, event_type: str, detail: dict[str, Any]) -> None:
        path = self._path(project_id, "events.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {"type": event_type, "detail": detail, "created_at": utc_now()}
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def list_events(self, project_id: str) -> list[dict[str, Any]]:
        path = self._path(project_id, "events.jsonl")
        if not path.is_file():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
