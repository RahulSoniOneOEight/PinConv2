"""Generation specs and the generation allow-list.

Generation is the last resort. It may never depict the product, a pack, a label
or a logo, and every generated asset must be disclosed.
"""

from __future__ import annotations

from ..models import Asset, AssetRoute
from .errors import MethodMatrixError
from .models import GenerationSpec, Method, TruthClass


def assert_generation_allowed(asset: Asset, truth_class: TruthClass) -> None:
    if truth_class in {TruthClass.EXACT, TruthClass.EXACT_TEXT, TruthClass.PROOF}:
        raise MethodMatrixError(
            f"{asset.id}: generation is not allowed for {truth_class.value} material"
        )
    if asset.route is not AssetRoute.TO_GENERATE:
        raise MethodMatrixError(f"{asset.id}: asset route does not permit generation")
    if not asset.rights.disclosure_required:
        raise MethodMatrixError(f"{asset.id}: generated media needs disclosure")


def build_generation_spec(asset: Asset, script: str) -> GenerationSpec:
    if asset.route is not AssetRoute.TO_GENERATE:
        raise MethodMatrixError(f"{asset.id}: generation spec requested for a non-generated asset")
    prompt = asset.generation_spec or "Synthetic narration for the approved script."
    return GenerationSpec(
        provider="runware",
        model="text-to-speech",
        prompt=f"{prompt} Script: {script}",
        seed=None,
        width=None,
        height=None,
        duration_seconds=20.0,
        reference_images=[],
        disclosure_required=True,
        disclosure_text="Synthetic voice disclosed in the delivery notes",
        cost_usd=0.0,
        budget_line_id=None,
    )


def method_for_generated(asset: Asset) -> Method:
    if asset.route is not AssetRoute.TO_GENERATE:
        raise MethodMatrixError(f"{asset.id}: not a generated asset")
    return Method.M7
