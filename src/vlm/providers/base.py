from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import VLMResponse


class VLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    def ask(self, image_path: str, question: str) -> VLMResponse: ...
