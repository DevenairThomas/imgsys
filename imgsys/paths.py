from pathlib import Path

def is_image_ext(path: Path, exts: set[str]) -> bool:
    """
    Return True if the file extension matches one of the given extensions.
    exts should be lowercase and include the leading dot.
    Example: {'.jpg', '.png'}
    """
    return path.suffix.lower() in exts