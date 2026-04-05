"""Custom exceptions for the CodeAtlas platform."""


class CodeAtlasError(Exception):
    """Base exception for all CodeAtlas errors."""

    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)
        self.message = message

    def __str__(self) -> str:
        return self.message


class AnalysisError(CodeAtlasError):
    """Raised when code analysis fails."""


class ConfigurationError(CodeAtlasError):
    """Raised when configuration is invalid or missing."""


class SchemaValidationError(CodeAtlasError):
    """Raised when a model fails schema validation."""


class LanguageNotSupportedError(CodeAtlasError):
    """Raised when a requested language is not supported."""

    def __init__(self, language: str) -> None:
        super().__init__(f"Language not supported: {language!r}")
        self.language = language


class FileDiscoveryError(CodeAtlasError):
    """Raised when file discovery fails."""


class SerializationError(CodeAtlasError):
    """Raised when JSON serialization or deserialization fails."""
