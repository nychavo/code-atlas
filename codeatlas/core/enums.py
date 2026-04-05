"""Enumerations used throughout the CodeAtlas platform."""

from enum import Enum


class Language(str, Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    UNKNOWN = "unknown"


class ArtifactType(str, Enum):
    """Types of code artifacts."""

    FILE = "file"
    MODULE = "module"
    PACKAGE = "package"


class SymbolKind(str, Enum):
    """Kinds of code symbols."""

    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    CONSTANT = "constant"
    GLOBAL = "global"
    IMPORT = "import"
    VARIABLE = "variable"


class DependencyKind(str, Enum):
    """Kinds of dependencies between code elements."""

    IMPORTS = "imports"
    INHERITS_FROM = "inherits_from"
    INSTANTIATES = "instantiates"
    CALLS = "calls"
    USES_TYPE = "uses_type"
    REFERENCES_CONSTANT = "references_constant"
    DECORATED_BY = "decorated_by"
    RAISES = "raises"
    CONFIGURED_BY = "configured_by"
    TEST_TARGETS = "test_targets"


class ArchitecturalLayer(str, Enum):
    """Architectural layers of the codebase."""

    API = "api"
    SERVICE = "service"
    REPOSITORY = "repository"
    MODEL = "model"
    CORE = "core"
    UTILS = "utils"
    WORKFLOW = "workflow"
    CONFIG = "config"
    TEST = "test"
    UNKNOWN = "unknown"


class ConfidenceLevel(float, Enum):
    """Confidence levels for analysis results."""

    HIGH = 0.95
    MEDIUM = 0.6
    LOW = 0.3
    UNKNOWN = 0.0


class DiagnosticSeverity(str, Enum):
    """Severity levels for diagnostic messages."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
