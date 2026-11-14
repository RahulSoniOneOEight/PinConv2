"""Unit tests for the Level 2 rules, catalogue, gate and local engine."""

from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

import pytest

from pinconv2.level2.catalogue import SOURCE_MAP
from pinconv2.level2.corrections import next_run_id, parse_jsonl
from pinconv2.level2.docx import DocxBuilder
from pinconv2.level2.engines.base import SpendLedger
from pinconv2.level2.engines.local import LocalEngine
from pinconv2.level2.engines.openmontage import OpenMontageEngine
from pinconv2.level2.errors import Level2Error, MethodMatrixError, RecipeError
from pinconv2.level2.licence_gate import (
    classify_licence,
    gate_candidate,
    gate_entry,
)
from pinconv2.level2.method_selector import assert_method_allowed
from pinconv2.level2.models import (
    GateVerdict,
    LicenceClass,
    Method,
    MethodCandidate,
    ProcessingOp,
    SourceStrategy,
    TruthClass,
)
from pinconv2.level2.recipes import build_recipe, validate_recipe
from pinconv2.models import (
    Asset,
    AssetRoute,
    Exactness,
    RightsRecord,
    RightsStatus,
    TechSpec,
)


def test_blocked_sources_stay_blocked() -> None:
    for source_id in ("bbc-sound-effects", "gadm"):
        entry = SOURCE_MAP[source_id]
        decision = gate_entry(entry)
        assert decision.verdict is GateVerdict.BLOCK
        assert decision.reasons


def test_share_alike_is_blocked() -> None:
    entry = SOURCE_MAP["openmoji"]
    assert entry.licence_class is LicenceClass.CC_BY_SA
    assert gate_entry(entry).verdict is GateVerdict.BLOCK


def test_manual_only_sources_are_never_scripted() -> None:
    assert SOURCE_MAP["free-music-archive"].scriptable is False
    assert SOURCE_MAP["videezy"].scriptable is False
    assert SOURCE_MAP["ccmixter"].scriptable is True


def test_classify_licence_prefers_the_restriction() -> None:
    assert classify_licence("CC BY-NC-SA 4.0") is LicenceClass.CC_BY_NC
    assert classify_licence("CC BY 4.0") is LicenceClass.CC_BY
    assert classify_licence("CC0") is LicenceClass.CC0
    assert classify_licence("public domain") is LicenceClass.PD
    assert classify_licence("something private") is LicenceClass.UNKNOWN


def test_aggregator_needs_origin_verification() -> None:
    candidate = MethodCandidate(
        candidate_id="CND-AS10-01",
        asset_id="AS-10",
        provider="openverse",
        url="https://openverse.example/track",
        licence_class=LicenceClass.CC0,
        fit_score=80,
        cost_usd=0,
    )
    held = gate_candidate(candidate)
    assert held.gate_verdict is GateVerdict.HOLD
    assert any("origin" in reason for reason in held.gate_reasons)

    verified = gate_candidate(
        candidate.model_copy(
            update={
                "origin_verified": True,
                "attribution": "Artist — track (CC0)",
            }
        )
    )
    assert verified.gate_verdict is GateVerdict.PASS


def test_cc_by_needs_attribution() -> None:
    candidate = MethodCandidate(
        candidate_id="CND-AS10-02",
        asset_id="AS-10",
        provider="ccmixter",
        url="https://ccmixter.org/files/x",
        licence_class=LicenceClass.CC_BY,
        fit_score=88,
        cost_usd=0,
    )
    held = gate_candidate(candidate)
    assert held.gate_verdict is GateVerdict.HOLD
    assert any("attribution" in reason for reason in held.gate_reasons)

    complete = gate_candidate(candidate.model_copy(update={"attribution": "Artist — track"}))
    assert complete.gate_verdict is GateVerdict.PASS


@pytest.mark.parametrize(
    ("truth_class", "method"),
    [
        (TruthClass.EXACT, Method.M1),
        (TruthClass.EXACT, Method.M5),
        (TruthClass.EXACT, Method.M7),
        (TruthClass.PROOF, Method.M1),
        (TruthClass.PROOF, Method.M5),
        (TruthClass.PROOF, Method.M7),
        (TruthClass.EXACT_TEXT, Method.M1),
        (TruthClass.ATMOSPHERIC, Method.M8),
    ],
)
def test_matrix_refuses_fake_product_media(truth_class: TruthClass, method: Method) -> None:
    with pytest.raises(MethodMatrixError):
        assert_method_allowed(truth_class, method, "test")


def test_matrix_allows_capture_of_the_original() -> None:
    with pytest.raises(MethodMatrixError):
        assert_method_allowed(TruthClass.EXACT, Method.M6, "test")
    assert_method_allowed(TruthClass.EXACT, Method.M6, "test", original_capture=True)
    assert_method_allowed(TruthClass.PROOF, Method.M6, "test")
    assert_method_allowed(TruthClass.PROOF, Method.M2, "test")


def test_representative_generation_needs_disclosure() -> None:
    with pytest.raises(MethodMatrixError):
        assert_method_allowed(TruthClass.REPRESENTATIVE, Method.M7, "test")
    assert_method_allowed(TruthClass.REPRESENTATIVE, Method.M7, "test", disclosed=True)


def _pack_asset() -> Asset:
    return Asset(
        id="AS-02",
        name="Easy Pour Mixed Bag pack",
        description="Front pack",
        route=AssetRoute.SUPPLIED,
        rights=RightsRecord(
            status=RightsStatus.NEEDS_APPROVAL,
            licence_name="Brand pack licence pending",
            commercial_use=True,
            modification=True,
        ),
        tech=TechSpec(format="JPEG", width=1800, height=1800),
        exactness=Exactness.EXACT,
    )


def test_exact_recipe_preserves_the_label() -> None:
    asset = _pack_asset()
    ops = build_recipe(asset, SourceStrategy.SUPPLIED)
    assert ops[0].op == "alpha_cutout"
    assert ops[0].params["preserve_label"] is True
    validate_recipe(asset, ops)


def test_recipe_refuses_to_crop_the_label() -> None:
    asset = _pack_asset()
    bad = [
        ProcessingOp(op="alpha_cutout", params={"preserve_label": False}),
        ProcessingOp(op="encode", params={"codec": "png"}),
    ]
    with pytest.raises(RecipeError):
        validate_recipe(asset, bad)


def test_recipe_refuses_unknown_ops() -> None:
    with pytest.raises(ValueError):
        ProcessingOp(op="magic_enhance", params={})


def test_local_engine_processes_audio(tmp_path: Path) -> None:
    source = tmp_path / "tone.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1:sample_rate=48000",
            "-c:a",
            "pcm_s16le",
            str(source),
        ],
        check=True,
        capture_output=True,
    )
    engine = LocalEngine()
    assert engine.available
    ops = [
        ProcessingOp(op="loudness_norm", params={"lufs": -16.0, "true_peak": -1.0}),
        ProcessingOp(op="encode", params={"codec": "pcm_s24le", "container": "wav"}),
    ]
    result = engine.process(ops, source, tmp_path / "processed.wav")
    assert result.probe.sample_rate == 48000
    assert result.probe.duration_seconds is not None
    assert 0.9 <= result.probe.duration_seconds <= 1.1
    assert len(result.sha256) == 64
    assert result.bytes > 0


def test_local_engine_assembles_clips(tmp_path: Path) -> None:
    clips: list[Path] = []
    for index, colour in enumerate(("red", "blue")):
        clip = tmp_path / f"clip-{index}.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c={colour}:s=320x180:d=0.5:r=25",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(clip),
            ],
            check=True,
            capture_output=True,
        )
        clips.append(clip)
    engine = LocalEngine()
    output = engine.assemble(clips, tmp_path / "rough-cut.mp4")
    probe = engine.probe(output)
    assert probe.width == 320 and probe.height == 180
    assert probe.duration_seconds is not None
    assert 0.9 <= probe.duration_seconds <= 1.2


def test_docx_writer_is_a_valid_package(tmp_path: Path) -> None:
    builder = DocxBuilder()
    builder.heading("Gate 2 review")
    builder.paragraph("Estimate: $87.40")
    builder.table(["Asset", "Status"], [["AS-02", "blocked"]])
    path = builder.save(tmp_path / "review.docx")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        assert "word/document.xml" in names
        document = archive.read("word/document.xml").decode("utf-8")
    assert "Gate 2 review" in document
    assert "AS-02" in document


def test_correction_run_numbering_and_parsing() -> None:
    assert next_run_id("rev-002") == "rev-003"
    with pytest.raises(Level2Error):
        next_run_id("draft")
    with pytest.raises(Level2Error):
        parse_jsonl("")
    with pytest.raises(Level2Error):
        parse_jsonl('{"id": "bad"}')


def test_method_candidate_rejects_bad_ids() -> None:
    with pytest.raises(ValueError):
        MethodCandidate(
            candidate_id="CND-1",
            asset_id="AS-2",
            provider="x",
            url="u",
            licence_class=LicenceClass.CC0,
            fit_score=50,
            cost_usd=0,
        )


def test_engine_search_gates_and_refuses_held_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pinconv2.level2.errors import LicenceBlockedError

    monkeypatch.setenv("OPENMONTAGE_ENABLED", "1")
    ledger = SpendLedger(tmp_path / "ledger.jsonl", authorised=True)

    def client(operation: str, payload: dict[str, object]) -> dict[str, object]:
        if operation == "stock.search":
            return {
                "candidates": [
                    {
                        "candidate_id": "CND-AS10-01",
                        "asset_id": "AS-10",
                        "provider": "openverse",
                        "url": "https://openverse.example/track",
                        "licence_class": "CC0",
                        "fit_score": 80,
                        "cost_usd": 0,
                    },
                    {
                        "candidate_id": "CND-AS10-02",
                        "asset_id": "AS-10",
                        "provider": "ccmixter",
                        "url": "https://ccmixter.example/track",
                        "licence_class": "CC-BY-NC",
                        "fit_score": 90,
                        "cost_usd": 0,
                    },
                ],
                "cost_usd": 0,
            }
        return {"path": str(tmp_path / "asset.bin"), "cost_usd": 0}

    engine = OpenMontageEngine(ledger, client)
    candidates = engine.search("AS-10", "warm indian coffee bed")
    assert candidates[0].gate_verdict is GateVerdict.HOLD
    assert candidates[1].gate_verdict is GateVerdict.BLOCK
    with pytest.raises(LicenceBlockedError):
        engine.acquire(candidates[0])
    with pytest.raises(LicenceBlockedError):
        engine.acquire(candidates[1])
    assert ledger.receipts() == 1  # only the search cleared its reservation


def test_ledger_summary_matches_entries(tmp_path: Path) -> None:
    ledger = SpendLedger(tmp_path / "ledger.jsonl", authorised=True)
    ledger.reserve("BL-001", 10.0, "music")
    ledger.receipt("BL-001", 9.5, "music")
    summary = ledger.summary()
    assert summary["reservations"] == 1
    assert summary["receipts"] == 1
    assert summary["open_reservations"] == 0
    assert summary["spent_usd"] == 9.5
    assert len(summary["entries"]) == 2
