
from typing import *

from abc import ABC, abstractmethod
from dataclasses import dataclass

class Fetcher(ABC):
    async def initialize(self): ...

    async def close(self): ...

    @abstractmethod
    async def fetch(self, url: str) -> str: ...


@dataclass
class ParseResult:
    links: List[str]
    product: Optional[dict]

class Parser(ABC):
    @abstractmethod
    def parse(self, link: str, html: str) -> ParseResult:
        ...

class Saver(ABC):
    @abstractmethod
    async def save(self, product: dict):
        ...
