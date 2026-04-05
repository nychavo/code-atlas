"""Pydantic models for code artifact data."""

from pydantic import BaseModel


class FileStats(BaseModel):
    """Statistics about a source file."""

    size_bytes: int
    line_count: int
    blank_line_count: int
    comment_line_count: int
    code_line_count: int


class ImportRecord(BaseModel):
    """Represents a single import statement."""

    import_id: str
    module: str
    names: list[str]
    alias: str | None
    is_from_import: bool
    is_stdlib: bool
    is_relative: bool
    line_number: int
    confidence: float = 1.0


class ExportRecord(BaseModel):
    """Represents a publicly exported symbol."""

    export_id: str
    name: str
    kind: str
    line_number: int
    is_public: bool


class ParameterRecord(BaseModel):
    """Represents a function or method parameter."""

    name: str
    annotation: str | None
    default: str | None
    kind: str


class MethodRecord(BaseModel):
    """Represents a class method."""

    method_id: str
    name: str
    qualified_name: str
    docstring: str | None
    decorators: list[str]
    parameters: list[ParameterRecord]
    return_annotation: str | None
    is_async: bool
    is_classmethod: bool
    is_staticmethod: bool
    is_property: bool
    is_abstract: bool
    line_start: int
    line_end: int
    local_variables: list[str]


class ClassRecord(BaseModel):
    """Represents a class definition."""

    class_id: str
    name: str
    qualified_name: str
    docstring: str | None
    decorators: list[str]
    base_classes: list[str]
    resolved_base_classes: list[str]
    methods: list[MethodRecord]
    class_variables: list[str]
    instance_variables: list[str]
    line_start: int
    line_end: int
    is_abstract: bool
    is_dataclass: bool
    is_pydantic: bool


class FunctionRecord(BaseModel):
    """Represents a top-level function definition."""

    function_id: str
    name: str
    qualified_name: str
    docstring: str | None
    decorators: list[str]
    parameters: list[ParameterRecord]
    return_annotation: str | None
    is_async: bool
    line_start: int
    line_end: int
    local_variables: list[str]


class ConstantRecord(BaseModel):
    """Represents a module-level constant (ALL_CAPS)."""

    constant_id: str
    name: str
    value_repr: str
    annotation: str | None
    line_number: int


class GlobalRecord(BaseModel):
    """Represents a module-level variable."""

    global_id: str
    name: str
    value_repr: str | None
    annotation: str | None
    line_number: int


class DependencyRecord(BaseModel):
    """Represents a dependency relationship between code elements."""

    dependency_id: str
    kind: str
    source: str
    target: str
    target_module: str | None
    confidence: float
    line_number: int | None
    evidence: str | None
    is_resolved: bool


class ReferenceRecord(BaseModel):
    """Represents a reference from one symbol to another."""

    reference_id: str
    name: str
    kind: str
    resolved_to: str | None
    owning_artifact: str | None
    confidence: float
    is_resolved: bool
    line_number: int | None


class SummaryRecord(BaseModel):
    """High-level summary of a code artifact."""

    purpose: str
    architectural_layer: str
    key_dependencies: list[str]
    key_exports: list[str]
    unresolved_areas: list[str]
    complexity_notes: list[str]


class MetadataRecord(BaseModel):
    """Metadata about the analysis run that produced an artifact."""

    created_at: str
    analyzer_version: str
    schema_version: str
    language: str
    encoding: str = "utf-8"
    has_errors: bool = False
    error_count: int = 0
    warning_count: int = 0


class Artifact(BaseModel):
    """Complete analysis artifact for a single source file."""

    schema_version: str
    project_id: str
    artifact_id: str
    artifact_type: str
    language: str
    path: str
    relative_path: str
    module_name: str
    hash: str
    file_stats: FileStats
    docstring: str | None
    summary: SummaryRecord
    imports: list[ImportRecord]
    exports: list[ExportRecord]
    classes: list[ClassRecord]
    functions: list[FunctionRecord]
    constants: list[ConstantRecord]
    globals: list[GlobalRecord]
    dependencies: list[DependencyRecord]
    references: list[ReferenceRecord]
    metadata: MetadataRecord
