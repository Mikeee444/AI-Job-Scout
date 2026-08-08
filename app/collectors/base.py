from abc import ABC, abstractmethod


class BaseCollector(ABC):
    """Base interface for all job collectors."""

    @abstractmethod
    def collect(self) -> list[dict]:
        """Collect and return normalized job data."""
        pass