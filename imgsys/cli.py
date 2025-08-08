import typer
from pathlib import Path
from rich import print
from imgsys.validate import emit_json_schemas
from imgsys.scanner import load_dataset_config, scan_collection, build_sidecar, write_sidecar, ensure_manifest
from imgsys.ids import stable_collection_id

app = typer.Typer(help="imgsys Phase 0 CLI")

@app.command()
def emit_schemas(out: Path = typer.Argument(Path("docs"))):
    emit_json_schemas(out)
    print(f"[green]Wrote JSON Schemas to {out}[/green]")

@app.command()
def ingest(collection: Path, cfg: Path = Path("configs/dataset.yaml")):
    cfgd = load_dataset_config(cfg)
    dataset_root = Path(cfgd["dataset_root"])
    collection_dir = collection.resolve()
    images, non_images = scan_collection(dataset_root, collection_dir, cfgd)
    coll_id = stable_collection_id(dataset_root, collection_dir)
    ensure_manifest(collection_dir, coll_id)

    written = 0
    for img in images:
        sidecar = build_sidecar(dataset_root, collection_dir, img, cfgd)
        write_sidecar(sidecar, collection_dir, img, cfgd)
        written += 1

    # update manifest counts
    manifest_path = collection_dir / "collection.json"
    import json
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["stats"]["total_files"] = len(images) + len(non_images)
    manifest["stats"]["images_found"] = len(images)
    manifest["stats"]["non_images_ignored"] = len(non_images)
    manifest["stats"]["sidecars_written"] = written
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"[green]Ingest complete[/green]: {written} sidecars, {len(non_images)} non-images ignored")

if __name__ == "__main__":
    app()