from pathlib import Path
from datetime import datetime, timezone
import yaml
from imgsys.paths import is_image_ext
from imgsys.ids import content_image_id, sha256_head, stable_collection_id
from imgsys.exif_utils import open_image_basic, read_exif
from imgsys.schema import ImageSidecar, CollectionManifest, IngestInfo, Fingerprint, Audit, Review

def utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")

def load_dataset_config(cfg_path: Path) -> dict:
    return yaml.safe_load(cfg_path.read_text())

def scan_collection(dataset_root: Path, collection_dir: Path, cfg: dict) -> tuple[list[Path], list[Path]]:
    exts = set(e.lower() for e in cfg["include_extensions"])
    ignore = cfg.get("ignore_globs", [])
    # simple filter first
    all_files = [p for p in collection_dir.rglob("*") if p.is_file()]
    # apply ignore
    from fnmatch import fnmatch
    files = [p for p in all_files if not any(fnmatch(p.as_posix(), g) for g in ignore)]
    images = [p for p in files if p.suffix.lower() in exts]
    non_images = [p for p in files if p not in images]
    return images, non_images

def build_sidecar(dataset_root: Path, collection_dir: Path, img_path: Path, cfg: dict) -> ImageSidecar:
    rel = img_path.relative_to(collection_dir).as_posix()
    # fingerprint
    head_bytes = cfg.get("fingerprint_head_bytes", 65536)
    stat = img_path.stat()
    fp = Fingerprint(size=stat.st_size, mtime=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat().replace("+00:00","Z"), sha256_head=sha256_head(img_path, head_bytes))
    # decode
    basic = open_image_basic(img_path)
    exif = read_exif(img_path)
    # ids
    image_id = content_image_id(img_path)
    collection_id = stable_collection_id(dataset_root, collection_dir)
    # ingest
    ingest = IngestInfo(
        filesize=stat.st_size,
        width=basic["width"],
        height=basic["height"],
        format=basic["format"],
        mode=basic["mode"],
        exif=exif,
        checksum=image_id,
        fingerprint=fp,
        discovered_at=utc_now(),
        source={"provenance": "local_folder", "original_path": str(img_path)}
    )
    review = Review(status="auto_ok", flags=[], notes="", history=[{"when": utc_now(), "who": "system", "what": "ingested"}])
    sidecar = ImageSidecar(
        image_id=image_id,
        collection_id=collection_id,
        relative_path=rel,
        ingest=ingest,
        context={"dir_hints": collection_dir.name.split("_"), "filename_hints": [img_path.stem]},
        audit=Audit(toolchain={}, last_modified=utc_now())
    )
    return sidecar

def write_sidecar(sidecar: ImageSidecar, collection_dir: Path, img_path: Path, cfg: dict) -> Path:
    sidecar_name = img_path.with_suffix(img_path.suffix + ".json").name  # e.g., image.jpg.json
    out_path = collection_dir / img_path.relative_to(collection_dir).parent / sidecar_name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(sidecar.model_dump_json(indent=2, by_alias=True), encoding="utf-8")
    return out_path

def ensure_manifest(collection_dir: Path, collection_id: str) -> Path:
    path = collection_dir / "collection.json"
    if not path.exists():
        manifest = CollectionManifest(
            collection_id=collection_id,
            discovered_at=utc_now(),
            stats={"total_files": 0, "images_found": 0, "non_images_ignored": 0, "sidecars_written": 0, "flagged": 0, "auto_ok": 0, "reviewed": 0},
            runs=[],
            notes=""
        )
        path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return path