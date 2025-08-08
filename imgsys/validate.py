from imgsys.schema import ImageSidecar, CollectionManifest
from pydantic.json_schema import models_json_schema
import json
from pathlib import Path

def emit_json_schemas(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for model, name in [(ImageSidecar, "schema_image.json"),
                        (CollectionManifest, "schema_collection.json")]:
        schema = model.model_json_schema()
        (out_dir / name).write_text(json.dumps(schema, indent=2), encoding="utf-8")