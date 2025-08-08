from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

SCHEMA_VERSION = "1.0.0"

class Fingerprint(BaseModel):
    size: int
    mtime: str
    sha256_head: str

class IngestInfo(BaseModel):
    filesize: int
    width: int
    height: int
    format: str
    mode: str
    exif: Dict[str, Any] | None = None
    checksum: str
    fingerprint: Fingerprint
    discovered_at: str
    source: Dict[str, Any] = Field(default_factory=dict)

class ModelCaption(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    run_id: Optional[str] = None
    output: Optional[str] = None
    confidence: Optional[float] = None

class ModelTags(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    run_id: Optional[str] = None
    labels: List[Dict[str, Any]] = Field(default_factory=list)

class ModelNSFW(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    run_id: Optional[str] = None
    score: Optional[float] = None
    clazz: Optional[str] = Field(default=None, alias="class")

class ModelOCR(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    run_id: Optional[str] = None
    text: Optional[str] = None
    blocks: Optional[List[Dict[str, Any]]] = None

class ModelStyle(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    run_id: Optional[str] = None
    anime_score: Optional[float] = None
    art_style: Optional[str] = None

class ModelPlaces(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    run_id: Optional[str] = None
    topk: List[Dict[str, Any]] = Field(default_factory=list)

class ModelFaces(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    run_id: Optional[str] = None
    num_faces: Optional[int] = None
    embeddings: Optional[List[List[float]]] = None  # optional later

class Models(BaseModel):
    caption: ModelCaption = ModelCaption()
    tags: ModelTags = ModelTags()
    nsfw: ModelNSFW = ModelNSFW()
    ocr: ModelOCR = ModelOCR()
    style: ModelStyle = ModelStyle()
    places: ModelPlaces = ModelPlaces()
    faces: ModelFaces = ModelFaces()

class Fusion(BaseModel):
    policy_version: Optional[str] = None
    decisions: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)

class Review(BaseModel):
    status: str = "auto_ok"  # auto_ok | needs_review | reviewed
    flags: List[str] = Field(default_factory=list)
    notes: str = ""
    history: List[Dict[str, Any]] = Field(default_factory=list)
    gold_labels: Any | None = None

class FinalFields(BaseModel):
    caption: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    locales: List[str] = Field(default_factory=list)

class Audit(BaseModel):
    toolchain: Dict[str, Any] = Field(default_factory=dict)
    last_modified: str

class ImageSidecar(BaseModel):
    schema_version: str = SCHEMA_VERSION
    image_id: str
    collection_id: str
    relative_path: str
    ingest: IngestInfo
    context: Dict[str, Any] = Field(default_factory=dict)
    models: Models = Models()
    fusion: Fusion = Fusion()
    review: Review = Review()
    final: FinalFields = FinalFields()
    audit: Audit

class RunInfo(BaseModel):
    run_id: str
    stages: List[str]
    models: Dict[str, Dict[str, str]]
    policy: Dict[str, Any] | None = None
    metrics: Any | None = None

class CollectionManifest(BaseModel):
    schema_version: str = SCHEMA_VERSION
    collection_id: str
    relative_path: str = "."
    discovered_at: str
    stats: Dict[str, int] = Field(default_factory=dict)
    runs: List[RunInfo] = Field(default_factory=list)
    notes: str = ""