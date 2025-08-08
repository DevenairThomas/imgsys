import hashlib
from pathlib import Path

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_head(path: Path, head_bytes: int) -> str:
    with path.open("rb") as f:
        return hashlib.sha256(f.read(head_bytes)).hexdigest()

def content_image_id(path: Path) -> str:
    return f"sha256:{sha256_file(path)}"

def stable_collection_id(dataset_root: Path, collection_dir: Path) -> str:
    rel = collection_dir.relative_to(dataset_root).as_posix()
    # normalize lower + forward slashes; hash as backup if needed
    return rel