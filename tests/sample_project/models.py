"""Sample domain models for the test project."""

from pydantic import BaseModel


class User(BaseModel):
    """Represents an application user."""

    id: int
    name: str
    email: str
    is_active: bool = True


class Product(BaseModel):
    """Represents a product in the catalogue."""

    id: int
    name: str
    price: float
    stock: int = 0

    def is_available(self) -> bool:
        """Return True if the product has stock."""
        return self.stock > 0
