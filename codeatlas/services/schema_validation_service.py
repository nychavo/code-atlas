"""Schema validation service — validates Pydantic models."""

import logging

from pydantic import BaseModel, ValidationError

from codeatlas.core.exceptions import SchemaValidationError


class SchemaValidationService:
    """Validates Pydantic model instances and raises on failure."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def validate(self, model: BaseModel) -> bool:
        """Return True if *model* is valid.

        This is a lightweight check; Pydantic already validates on
        construction, but this method can be used to re-validate after
        manual attribute mutation.
        """
        try:
            model.__class__.model_validate(model.model_dump())
            return True
        except ValidationError as exc:
            self.logger.error("Validation failed: %s", exc)
            return False

    def validate_or_raise(self, model: BaseModel) -> None:
        """Validate *model* and raise :class:`~codeatlas.core.exceptions.SchemaValidationError` if invalid."""
        try:
            model.__class__.model_validate(model.model_dump())
        except ValidationError as exc:
            raise SchemaValidationError(str(exc)) from exc
