"""JSON serialisation helpers for Pydantic models."""

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class JsonHelper:
    """Static utility methods for reading and writing JSON files."""

    @staticmethod
    def write_model(model: BaseModel, path: Path, indent: int = 2) -> None:
        """Serialise a Pydantic model to a JSON file at *path*."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(model.model_dump_json(indent=indent))

    @staticmethod
    def read_model(path: Path, model_class: type[T]) -> T:
        """Deserialise a JSON file at *path* into a Pydantic model instance."""
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return model_class.model_validate(data)

    @staticmethod
    def write_dict(data: dict, path: Path, indent: int = 2) -> None:
        """Write a plain dictionary to a JSON file at *path*."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=indent, default=str)

    @staticmethod
    def read_dict(path: Path) -> dict:
        """Read a JSON file at *path* and return it as a plain dictionary."""
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
