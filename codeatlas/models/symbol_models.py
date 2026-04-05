"""Pydantic models for the symbol index."""

from pydantic import BaseModel


class SymbolEntry(BaseModel):
    """An entry in the project-wide symbol index."""

    symbol_id: str
    name: str
    qualified_name: str
    kind: str
    language: str
    owning_artifact: str
    path: str
    line_number: int | None
    is_public: bool


class SymbolIndex(BaseModel):
    """Project-wide index of all known symbols."""

    schema_version: str
    project_id: str
    symbols: dict[str, SymbolEntry]
    metadata: dict
