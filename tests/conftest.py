import pytest

from gemini_wrapper import GeminiWrapper


@pytest.fixture
def gemini() -> GeminiWrapper:
    return GeminiWrapper()
