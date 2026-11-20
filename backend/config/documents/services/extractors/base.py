from typing import BinaryIO, Protocol


class TextExtractor(Protocol):
    """Contract for document text extractors."""
    def extract(self, file: BinaryIO) -> str:
        """Extract text from a binary file-like object."""
        