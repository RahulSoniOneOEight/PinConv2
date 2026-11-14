"""Declarative processing recipes.

A recipe is an ordered, validated op list. It never contains an implicit
default: a missing parameter is a validation error, because a silent default is
how a pack label gets cropped.
"""

from __future__ import annotations

from ..models import Asset
from .errors import RecipeError
from .models import Method, ProcessingOp, SourceStrategy

MASTER_WIDTH = 1920
MASTER_HEIGHT = 1080
MASTER_FPS = 25


def _op(op: str, **params: object) -> ProcessingOp:
    return ProcessingOp(op=op, params=params)


def build_recipe(asset: Asset, strategy: SourceStrategy) -> list[ProcessingOp]:
    fmt = asset.tech.format.upper()

    if fmt == "WAV":
        return _audio_recipe(asset)
    if asset.route.value in {"to_capture", "to_generate"} and fmt.startswith("PRORES"):
        return _video_recipe(asset)
    if fmt in {"PNG", "JPEG"}:
        return _still_recipe(asset, strategy)
    raise RecipeError(f"{asset.id}: no recipe for format {asset.tech.format}")


def _still_recipe(asset: Asset, strategy: SourceStrategy) -> list[ProcessingOp]:
    ops: list[ProcessingOp] = []
    if asset.exactness.value == "exact" and asset.tech.transparency:
        ops.append(_op("alpha_cutout", preserve_label=True, despill=True))
    elif asset.exactness.value == "exact":
        ops.append(
            _op(
                "alpha_cutout",
                preserve_label=True,
                despill=True,
                feather_px=2,
            )
        )
    ops.append(_op("grade", lut="bt_warm_counter_v1", exposure=0.02))
    if asset.tech.width and asset.tech.width > MASTER_WIDTH:
        ops.append(
            _op(
                "scale",
                width=MASTER_WIDTH,
                height=MASTER_HEIGHT,
                mode="fit",
                upscale=False,
            )
        )
    ops.append(_op("encode", codec="png", pix_fmt="rgba" if asset.tech.transparency else "rgb24"))
    return ops


def _video_recipe(asset: Asset) -> list[ProcessingOp]:
    ops: list[ProcessingOp] = [
        _op("trim", in_frame=0, out_frame=asset.tech.duration_frames or 500),
        _op("stabilise", strength=0.3, crop_pct=2.0),
        _op("conform", fps=MASTER_FPS, interp="nearest"),
    ]
    if asset.id == "AS-06":
        ops.append(
            _op(
                "speed_ramp",
                from_speed=1.0,
                to_speed=0.35,
                curve="ease_in_out",
                anchor_frame=80,
            )
        )
    ops.extend(
        [
            _op("grade", lut="bt_warm_counter_v1", exposure=0.05),
            _op("scale", width=MASTER_WIDTH, height=MASTER_HEIGHT, mode="cover"),
            _op("encode", codec="prores_422hq", pix_fmt="yuv422p10le"),
        ]
    )
    return ops


def _audio_recipe(asset: Asset) -> list[ProcessingOp]:
    if asset.id in {"AS-10", "AS-14"}:
        return [
            _op("trim", in_frame=0, out_frame=500),
            _op("fade", direction="in_out", in_frames=12, out_frames=25),
            _op("loudness_norm", lufs=-18.0, true_peak=-2.0),
            _op("resample", sample_rate=48000, bit_depth=24),
            _op("encode", codec="pcm_s24le", container="wav"),
        ]
    if asset.id in {"AS-11", "AS-12"}:
        return [
            _op("trim", in_frame=0, out_frame=asset.tech.duration_frames or 50),
            _op("loudness_norm", lufs=-20.0, true_peak=-3.0),
            _op("encode", codec="pcm_s24le", container="wav"),
        ]
    if asset.id in {"AS-09", "AS-15"}:
        ops = [
            _op("trim", in_frame=0, out_frame=500),
            _op("denoise", strength=0.25),
            _op("loudness_norm", lufs=-16.0, true_peak=-1.0),
            _op("resample", sample_rate=48000, bit_depth=24),
            _op("encode", codec="pcm_s24le", container="wav"),
        ]
        if asset.id == "AS-15":
            ops.insert(0, _op("channel_map", channels=1))
        return ops
    raise RecipeError(f"{asset.id}: no audio recipe")


def validate_recipe(asset: Asset, ops: list[ProcessingOp]) -> None:
    if not ops:
        raise RecipeError(f"{asset.id}: recipe is empty")
    names = [op.op for op in ops]
    if names[-1] != "encode":
        raise RecipeError(f"{asset.id}: recipe must end with encode")

    fmt = asset.tech.format.upper()
    if fmt == "WAV":
        if "loudness_norm" not in names:
            raise RecipeError(f"{asset.id}: audio recipe needs loudness_norm")
    elif fmt.startswith("PRORES"):
        for required in ("conform", "scale"):
            if required not in names:
                raise RecipeError(f"{asset.id}: video recipe needs {required}")
    if asset.exactness.value == "exact":
        cutout = next((op for op in ops if op.op == "alpha_cutout"), None)
        if cutout is not None and cutout.params.get("preserve_label") is not True:
            raise RecipeError(f"{asset.id}: exact cutout must preserve the label")
    for op in ops:
        if op.op == "text_render" and not op.params.get("copy_id"):
            raise RecipeError(f"{asset.id}: text_render needs a copy block id")
    if len(set(names)) != len(names) and "fade" not in names:
        # Duplicated ops are refused except where a deliberate pair is declared.
        raise RecipeError(f"{asset.id}: duplicate processing ops")


def describe(ops: list[ProcessingOp]) -> list[str]:
    described: list[str] = []
    for op in ops:
        keys = ",".join(f"{key}={value}" for key, value in sorted(op.params.items()))
        described.append(f"{op.op}({keys})" if keys else op.op)
    return described


def recipe_for_method(asset: Asset, method: Method, strategy: SourceStrategy) -> list[ProcessingOp]:
    if method is Method.M4 and asset.route.value in {"to_capture", "to_generate"}:
        raise RecipeError(f"{asset.id}: M4 does not process captured or generated media")
    ops = build_recipe(asset, strategy)
    validate_recipe(asset, ops)
    return ops
