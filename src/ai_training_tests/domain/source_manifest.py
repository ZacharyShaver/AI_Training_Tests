from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceBuildSpec:
    family: str
    source_label: str
    dataset_name: str
    parser_script: str | None
    output_group: str
    parser_args: tuple[str, ...] = ()


BASE_SOURCES: tuple[SourceBuildSpec, ...] = (
    SourceBuildSpec(
        family="esoteric",
        source_label="The Key to Theosophy",
        dataset_name="full_dialogue_dataset",
        parser_script=None,
        output_group="base",
    ),
    SourceBuildSpec(
        family="esoteric",
        source_label="The Corpus Hermeticum",
        dataset_name="full_dialogue_dataset",
        parser_script=None,
        output_group="base",
    ),
    SourceBuildSpec(
        family="buddhist",
        source_label="Milinda Panha",
        dataset_name="full_dialogue_dataset",
        parser_script=None,
        output_group="base",
    ),
    SourceBuildSpec(
        family="buddhist",
        source_label="Platform Sutra",
        dataset_name="full_dialogue_dataset",
        parser_script=None,
        output_group="base",
    ),
)


APPROVED_SOURCE_SPECS: tuple[SourceBuildSpec, ...] = (
    *BASE_SOURCES,
    SourceBuildSpec(
        family="buddhist",
        source_label="The Gateless Gate",
        dataset_name="gateless_gate_dialogue",
        parser_script="parse_gateless_gate.py",
        output_group="new_buddhist",
        parser_args=("--include-internal-dialogue",),
    ),
    SourceBuildSpec(
        family="buddhist",
        source_label="The Diamond Sutra",
        dataset_name="diamond_sutra_dialogue",
        parser_script="parse_diamond_sutra.py",
        output_group="new_buddhist",
    ),
    SourceBuildSpec(
        family="buddhist",
        source_label="Udana",
        dataset_name="udana_exclamation_dialogue",
        parser_script="parse_udana.py",
        output_group="new_buddhist",
        parser_args=("--final-only",),
    ),
    SourceBuildSpec(
        family="buddhist",
        source_label="Sutta Nipata",
        dataset_name="sutta_nipata_dialogue",
        parser_script="parse_sutta_nipata.py",
        output_group="new_buddhist",
    ),
    SourceBuildSpec(
        family="buddhist",
        source_label="Majjhima Nikaya",
        dataset_name="majjhima_nikaya_dialogue",
        parser_script="parse_majjhima_nikaya.py",
        output_group="new_buddhist",
    ),
    SourceBuildSpec(
        family="buddhist",
        source_label="Itivuttaka",
        dataset_name="itivuttaka_dialogue",
        parser_script="parse_itivuttaka.py",
        output_group="new_buddhist",
    ),
    SourceBuildSpec(
        family="buddhist",
        source_label="Zen Koans Database",
        dataset_name="zen_koans_database_clean_dialogue",
        parser_script="parse_zen_koans_database.py",
        output_group="new_buddhist",
    ),
    SourceBuildSpec(
        family="buddhist",
        source_label="Vimalakirti Nirdesa Sutra",
        dataset_name="vimalakirti_dialogue",
        parser_script="parse_vimalakirti.py",
        output_group="new_buddhist",
    ),
    SourceBuildSpec(
        family="esoteric",
        source_label="Asclepius",
        dataset_name="asclepius_dialogue",
        parser_script="parse_asclepius.py",
        output_group="new_esoteric",
    ),
)


def approved_source_labels() -> set[str]:
    return {spec.source_label for spec in APPROVED_SOURCE_SPECS}


def source_labels_for_family(family: str) -> set[str]:
    return {spec.source_label for spec in APPROVED_SOURCE_SPECS if spec.family == family}


def specs_for_output_group(output_group: str) -> list[SourceBuildSpec]:
    return [spec for spec in APPROVED_SOURCE_SPECS if spec.output_group == output_group]


def output_path_for_spec(
    spec: SourceBuildSpec,
    *,
    output_dir: Path,
    new_buddhist_dir: Path,
    new_esoteric_dir: Path,
) -> Path:
    if spec.output_group == "base":
        return output_dir / f"{spec.dataset_name}.jsonl"
    if spec.output_group == "new_buddhist":
        return new_buddhist_dir / f"{spec.dataset_name}.jsonl"
    if spec.output_group == "new_esoteric":
        return new_esoteric_dir / f"{spec.dataset_name}.jsonl"
    raise ValueError(f"Unknown output group: {spec.output_group}")

