from abc import ABC, abstractmethod


class DocstringTemplate(ABC):
    """
    Base interface for docstring templates.
    """

    @abstractmethod
    def render_function(self, name: str, summary: str, args: list, returns: str | None) -> str:
        pass

    @abstractmethod
    def render_class(self, name: str, summary: str) -> str:
        pass
