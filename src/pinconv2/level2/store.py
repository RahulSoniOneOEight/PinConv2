"""Run storage for Level 2.

Layout::

    projects/<project_id>/level2/runs/<run_id>/
      run.json
      asset-intents.json
      layer-method-decisions.json
      asset-production-tasks.json
      capture-plan.json
      sound-plan.json
      budget-estimate.json
      flow.json
      build-sheet/...
      qc/...
      gate2/packet-2a.json
      review-pack.md

Runs are immutable by convention: a correction creates a new run identifier
rather than editing an approved one.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from pydantic import BaseModel

from ..errors import NotFoundError, StoreError
from ..models import ProductionPlan, utc_now
from .build_sheet import render_build_sheet, render_captions
from .docx import DocxBuilder
from .models import BuildSheet, FileDigest, Level2Plan
from .review_pack import (
    render_budget,
    render_budget_docx,
    render_feedback_form,
    render_review,
    render_review_docx,
)

_RUN_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,30}$")


class Level2RunStore:
    def __init__(self, project_dir: Path) -> None:
        self.root = Path(project_dir).resolve() / "level2"

    def run_dir(self, run_id: str) -> Path:
        if not _RUN_PATTERN.fullmatch(run_id):
            raise StoreError(f"invalid run id: {run_id!r}")
        return self.root / "runs" / run_id

    def _path(self, run_id: str, relative: str) -> Path:
        target = (self.run_dir(run_id) / relative).resolve()
        if not target.is_relative_to(self.run_dir(run_id)):
            raise StoreError(f"path escapes the run directory: {relative!r}")
        return target

    def _write_text(self, run_id: str, relative: str, text: str) -> Path:
        path = self._path(run_id, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        temporary.replace(path)
        return path

    def write_text(self, run_id: str, relative: str, text: str) -> Path:
        return self._write_text(run_id, relative, text)

    def write_json(self, run_id: str, relative: str, model: BaseModel) -> Path:
        return self._write_text(run_id, relative, model.model_dump_json(indent=2) + "\n")

    def write_data(self, run_id: str, relative: str, payload: object) -> Path:
        return self._write_text(
            run_id, relative, json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )

    def read_json(self, run_id: str, relative: str, model_type: type[BaseModel]) -> BaseModel:
        path = self._path(run_id, relative)
        if not path.is_file():
            raise NotFoundError(f"record not found: {path}")
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))

    def read_level2(self, run_id: str) -> Level2Plan:
        model = self.read_json(run_id, "run.json", Level2Plan)
        assert isinstance(model, Level2Plan)
        return model

    def read_build_sheet(self, run_id: str) -> BuildSheet:
        model = self.read_json(run_id, "build-sheet/build-sheet.json", BuildSheet)
        assert isinstance(model, BuildSheet)
        return model

    def digest(self, path: Path) -> FileDigest:
        payload = path.read_bytes()
        return FileDigest(sha256=hashlib.sha256(payload).hexdigest(), bytes=len(payload))

    def append_event(self, run_id: str, event_type: str, detail: dict[str, object]) -> None:
        path = self._path(run_id, "events.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {"type": event_type, "detail": detail, "created_at": utc_now()}
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def write_build_sheet(self, run_id: str, sheet: BuildSheet, plan: ProductionPlan) -> BuildSheet:
        base = "build-sheet"
        parts: dict[str, FileDigest] = {}

        for asset in sheet.assets:
            relative = f"{base}/assets/{asset.asset_id}.json"
            parts[relative] = self.digest(self.write_json(run_id, relative, asset))
        for shot in sheet.shots:
            relative = f"{base}/shots/{shot.shot_id}.json"
            parts[relative] = self.digest(self.write_json(run_id, relative, shot))
        for variant in sheet.variants:
            relative = f"{base}/variants/{variant.variant_id}.json"
            parts[relative] = self.digest(self.write_json(run_id, relative, variant))

        relative = f"{base}/timeline/timeline.json"
        parts[relative] = self.digest(self.write_json(run_id, relative, sheet.timeline))

        for name, content in render_captions(plan).items():
            relative = f"{base}/captions/{name}"
            parts[relative] = self.digest(self.write_text(run_id, relative, content))

        if sheet.corrections:
            relative = f"{base}/corrections.json"
            parts[relative] = self.digest(
                self.write_data(
                    run_id,
                    relative,
                    [item.model_dump(mode="json") for item in sheet.corrections],
                )
            )

        manifest = sheet.manifest.model_copy(update={"parts": parts})
        updated = sheet.model_copy(update={"manifest": manifest})

        self.write_json(run_id, f"{base}/manifest.json", manifest)
        self.write_json(run_id, f"{base}/build-sheet.json", updated)
        self.write_text(
            run_id, f"{base}/production-build-sheet.md", render_build_sheet(updated, plan)
        )
        self._write_build_sheet_docx(run_id, updated, plan)
        return updated

    def _write_build_sheet_docx(self, run_id: str, sheet: BuildSheet, plan: ProductionPlan) -> Path:
        manifest = sheet.manifest
        builder = DocxBuilder()
        builder.heading(f"Production build sheet — {plan.project_id}")
        builder.paragraph(f"Run {run_id} · plan revision {plan.revision}")
        builder.paragraph(f"Source plan hash: {manifest.source_plan_hash}")
        builder.heading("Budget", 2)
        builder.table(
            ["Item", "Value"],
            [
                ["Estimated total", f"${manifest.budget.total_usd:,.2f}"],
                ["Worst case", f"${manifest.budget.worst_usd:,.2f}"],
                ["Cap", f"${manifest.budget.cap_usd:,.2f}"],
                ["Headroom", f"${manifest.budget.headroom_usd:,.2f}"],
            ],
        )
        builder.heading("Assets", 2)
        builder.table(
            ["Asset", "Class", "Method", "Status", "Rights"],
            [
                [
                    asset.asset_id,
                    asset.truth_class.value,
                    "/".join(method.value for method in asset.methods),
                    asset.status.value,
                    asset.rights_status,
                ]
                for asset in sheet.assets
            ],
        )
        path = self._path(run_id, "build-sheet/production-build-sheet.docx")
        path.parent.mkdir(parents=True, exist_ok=True)
        return builder.save(path)

    def write_documents(
        self,
        run_id: str,
        plan: ProductionPlan,
        level2: Level2Plan,
        sheet: BuildSheet,
    ) -> None:
        self.write_text(run_id, "budget-estimate.md", render_budget(level2.budget, plan))
        render_budget_docx(level2.budget, plan).save(self._path(run_id, "budget-estimate.docx"))
        self.write_text(
            run_id,
            "review-pack.md",
            render_review(
                plan,
                level2.intents,
                level2.decisions,
                level2.budget,
                sheet,
                level2.variants,
            ),
        )
        render_review_docx(plan, level2.intents, level2.decisions, level2.budget, sheet).save(
            self._path(run_id, "review-pack.docx")
        )
        self.write_text(run_id, "feedback-form.md", render_feedback_form(plan, sheet))
