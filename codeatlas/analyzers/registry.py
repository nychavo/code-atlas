"""Language analyzer registry."""


class LanguageRegistry:
    """Registry mapping language names to analyzer classes."""

    _registry: dict[str, type] = {}

    @classmethod
    def register(cls, language: str, analyzer_class: type) -> None:
        """Register *analyzer_class* for *language*."""
        cls._registry[language.lower()] = analyzer_class

    @classmethod
    def get(cls, language: str) -> type | None:
        """Return the analyzer class for *language*, or None if not registered."""
        return cls._registry.get(language.lower())

    @classmethod
    def supported_languages(cls) -> list[str]:
        """Return a list of registered language names."""
        return list(cls._registry.keys())

    @classmethod
    def is_supported(cls, language: str) -> bool:
        """Return True if *language* has a registered analyzer."""
        return language.lower() in cls._registry
