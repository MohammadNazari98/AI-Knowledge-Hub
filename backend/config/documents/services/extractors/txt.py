from typing import BinaryIO


class TXTExtractor:
    def extract(self, file: BinaryIO) -> str:
        return file.read().decode("utf-8-sig")