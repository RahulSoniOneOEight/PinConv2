"""Verify the approved handoff before any planning starts."""

from __future__ import annotations

from ...store import ProjectStore
from ..handoff import ApprovedInputs, load_approved_inputs


class HandoffValidator:
    def validate(self, store: ProjectStore, project_id: str, revision: int) -> ApprovedInputs:
        return load_approved_inputs(store, project_id, revision)
