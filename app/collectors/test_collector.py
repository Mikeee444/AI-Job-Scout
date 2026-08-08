from .base import BaseCollector


class TestCollector(BaseCollector):

    def collect(self) -> list[dict]:
        return [
            {
                "title": "Junior Python Developer",
                "company": "Test Company",
                "location": "Graz, Austria",
                "salary": "€3,000",
                "url": "https://example.com/test-job",
                "description": "Python development and software testing.",
            }
        ]