"""Production flow: dependency graph, batches and critical path."""

from __future__ import annotations

from collections import deque

from ..models import ProductionPlan
from .errors import FlowError
from .models import AssetProductionTask, Batch, BuildSheet, FlowGraph, FlowNode

_NOMINAL_FRAMES = {
    "supplied": 20,
    "owned": 10,
    "capture": 120,
    "stock": 30,
    "generate": 60,
    "procedural": 30,
}

_BATCH_BY_STRATEGY = {
    "supplied": Batch.B1,
    "owned": Batch.B1,
    "capture": Batch.B2,
    "stock": Batch.B4,
    "generate": Batch.B4,
    "procedural": Batch.B3,
}


def _batch_for_task(task: AssetProductionTask) -> Batch:
    return _BATCH_BY_STRATEGY[task.source_strategy.value]


def build_flow(
    plan: ProductionPlan,
    tasks: list[AssetProductionTask],
    build_sheet: BuildSheet | None = None,
) -> FlowGraph:
    nodes: dict[str, FlowNode] = {}

    nodes["CAP-01"] = FlowNode(
        node_id="CAP-01",
        kind="capture",
        batch=Batch.B2,
        dependencies=[],
        duration_frames=240,
    )

    for task in tasks:
        nodes[task.asset_id] = FlowNode(
            node_id=task.asset_id,
            kind="asset",
            batch=_batch_for_task(task),
            dependencies=list(task.flow.dependencies),
            duration_frames=_NOMINAL_FRAMES.get(task.source_strategy.value, 30),
        )

    for shot in plan.shots:
        deps: list[str] = []
        for layer_id in shot.layer_ids:
            layer = plan.layer_map[layer_id]
            if (
                layer.binding_kind.value == "asset"
                and layer.binding_ref
                and layer.binding_ref not in deps
            ):
                deps.append(layer.binding_ref)
        nodes[shot.id] = FlowNode(
            node_id=shot.id,
            kind="shot",
            batch=Batch.B5,
            dependencies=deps,
            duration_frames=shot.end_frame - shot.start_frame,
        )

    audio_assets = [
        task.asset_id
        for task in tasks
        if task.source_strategy.value in {"stock", "supplied", "owned"}
        and plan.asset_map[task.asset_id].tech.format.upper() == "WAV"
    ]
    nodes["MIX-01"] = FlowNode(
        node_id="MIX-01",
        kind="audio",
        batch=Batch.B4,
        dependencies=audio_assets,
        duration_frames=60,
    )
    nodes["CAPTIONS-01"] = FlowNode(
        node_id="CAPTIONS-01",
        kind="audio",
        batch=Batch.B5,
        dependencies=["MIX-01"],
        duration_frames=30,
    )

    if build_sheet is not None and build_sheet.variants:
        for variant in build_sheet.variants:
            nodes[variant.variant_id] = FlowNode(
                node_id=variant.variant_id,
                kind="variant",
                batch=Batch.B5,
                dependencies=[shot.id for shot in plan.shots] + ["CAPTIONS-01"],
                duration_frames=variant.frame_count,
            )

    batches: dict[str, list[str]] = {}
    for node in nodes.values():
        batches.setdefault(node.batch.value, []).append(node.node_id)
    for ids in batches.values():
        ids.sort()

    order = _topological_order(nodes)
    critical = _critical_path(nodes, order)
    marked = [
        node.model_copy(update={"critical_path": node.node_id in critical})
        for node in nodes.values()
    ]
    marked.sort(key=lambda node: (node.batch.value, node.node_id))

    return FlowGraph(
        nodes=marked,
        batches=batches,
        critical_path=critical,
        acyclic=len(order) == len(nodes),
    )


def _topological_order(nodes: dict[str, FlowNode]) -> list[str]:
    incoming: dict[str, int] = {node_id: 0 for node_id in nodes}
    outgoing: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for node in nodes.values():
        for dependency in node.dependencies:
            if dependency not in nodes:
                raise FlowError(f"{node.node_id} depends on unknown node {dependency}")
            incoming[node.node_id] += 1
            outgoing[dependency].append(node.node_id)

    queue = deque(sorted(node_id for node_id, count in incoming.items() if count == 0))
    order: list[str] = []
    while queue:
        node_id = queue.popleft()
        order.append(node_id)
        for child in sorted(outgoing[node_id]):
            incoming[child] -= 1
            if incoming[child] == 0:
                queue.append(child)
    if len(order) != len(nodes):
        raise FlowError("the production graph has a cycle")
    return order


def _critical_path(nodes: dict[str, FlowNode], order: list[str]) -> list[str]:
    longest: dict[str, int] = {}
    previous: dict[str, str | None] = {}
    for node_id in order:
        node = nodes[node_id]
        best = 0
        best_parent: str | None = None
        for dependency in node.dependencies:
            candidate = longest[dependency] + nodes[dependency].duration_frames
            if candidate > best:
                best = candidate
                best_parent = dependency
        longest[node_id] = best
        previous[node_id] = best_parent

    if not order:
        return []
    end = max(order, key=lambda node_id: longest[node_id] + nodes[node_id].duration_frames)
    path: list[str] = []
    cursor: str | None = end
    while cursor is not None:
        path.append(cursor)
        cursor = previous[cursor]
    path.reverse()
    return path


def reachable(nodes: dict[str, FlowNode], start: str, target: str) -> bool:
    dependents: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for node in nodes.values():
        for dependency in node.dependencies:
            if dependency in dependents:
                dependents[dependency].append(node.node_id)
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current == target:
            return True
        for dependent in dependents[current]:
            if dependent not in seen:
                seen.add(dependent)
                queue.append(dependent)
    return False


def validate_flow(plan: ProductionPlan, flow: FlowGraph) -> None:
    if not flow.acyclic:
        raise FlowError("the production graph must be acyclic")
    nodes = {node.node_id: node for node in flow.nodes}
    for asset in plan.assets:
        if asset.id not in nodes:
            raise FlowError(f"the flow is missing asset node {asset.id}")
    for shot in plan.shots:
        if shot.id not in nodes:
            raise FlowError(f"the flow is missing shot node {shot.id}")
        for layer_id in shot.layer_ids:
            layer = plan.layer_map[layer_id]
            if layer.binding_kind.value != "asset" or not layer.binding_ref:
                continue
            if not reachable(nodes, layer.binding_ref, shot.id):
                raise FlowError(f"{layer.binding_ref} must be upstream of {shot.id} for {layer_id}")
