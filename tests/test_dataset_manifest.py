from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "config/dataset_manifest.json"


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_final_dataset_paths_exist_and_targets_are_1200() -> None:
    manifest = load_manifest()

    assert manifest["goals"]["buddhist_lines"] == 1200
    assert manifest["goals"]["occult_lines"] == 1200

    final_datasets = manifest["final_datasets"]
    assert final_datasets["buddhist"]["family"] == "buddhist"
    assert final_datasets["occult"]["family"] == "occult"
    assert final_datasets["combined"]["family"] == "combined"

    for dataset in final_datasets.values():
        dataset_path = REPO_ROOT / dataset["path"]
        assert dataset_path.exists(), dataset_path


def test_sources_include_parser_and_vault_note_paths() -> None:
    manifest = load_manifest()

    source_names = {source["source"] for source in manifest["sources"]}
    assert "The Gateless Gate" in source_names
    assert "The Key to Theosophy" in source_names

    for source in manifest["sources"]:
        assert source["family"] in {"buddhist", "occult"}
        assert source["final_dataset"]
        assert source["parser"]
        assert source["vault_note"].startswith("Obsidian/Projects/AI_Training_Tests/")
