"""Sample services for the test project."""

from tests.sample_project.models import Product, User

_USER_DB: dict[int, User] = {}
_PRODUCT_DB: dict[int, Product] = {}


class UserService:
    """Manages user lifecycle operations."""

    def create(self, user_id: int, name: str, email: str) -> User:
        """Create and store a new User."""
        user = User(id=user_id, name=name, email=email)
        _USER_DB[user_id] = user
        return user

    def get(self, user_id: int) -> User | None:
        """Return the User with *user_id*, or None."""
        return _USER_DB.get(user_id)

    def deactivate(self, user_id: int) -> bool:
        """Deactivate a user. Returns True if the user existed."""
        user = _USER_DB.get(user_id)
        if user is None:
            return False
        _USER_DB[user_id] = user.model_copy(update={"is_active": False})
        return True


class ProductService:
    """Manages product catalogue operations."""

    def add(self, product_id: int, name: str, price: float, stock: int = 0) -> Product:
        """Add a new product to the catalogue."""
        product = Product(id=product_id, name=name, price=price, stock=stock)
        _PRODUCT_DB[product_id] = product
        return product

    def get(self, product_id: int) -> Product | None:
        """Return the Product with *product_id*, or None."""
        return _PRODUCT_DB.get(product_id)

    def list_available(self) -> list[Product]:
        """Return all products that currently have stock."""
        return [p for p in _PRODUCT_DB.values() if p.is_available()]
