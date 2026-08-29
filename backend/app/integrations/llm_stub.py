"""
LLM Stub — future AI boundary.
Honest: no LLM installed. This stub shows where LLM would be called.
"""


class LLMStub:
    @staticmethod
    def generate(prompt: str) -> str:
        # Deterministic placeholder — never claims to be real AI
        return f"[LLM Stub] Prompt received ({len(prompt)} chars). Real LLM not integrated. Rule-based advisor is active."

    @staticmethod
    def is_available() -> bool:
        return False
