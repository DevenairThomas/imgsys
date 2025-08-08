from PIL import Image, UnidentifiedImageError
import piexif
from pathlib import Path

def open_image_basic(path: Path):
    try:
        with Image.open(path) as im:
            im.load()  # force decode header
            return {
                "width": im.width,
                "height": im.height,
                "format": im.format or "UNKNOWN",
                "mode": im.mode
            }
    except UnidentifiedImageError as e:
        raise RuntimeError(f"Decode error: {e}")

def read_exif(path: Path):
    try:
        exif_dict = piexif.load(str(path))
        # keep it lightweight; you can prune further
        return {k: v for k, v in exif_dict.items() if v}
    except Exception:
        return None