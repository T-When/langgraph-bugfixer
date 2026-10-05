from pydantic import BaseModel, Field


class CodeFixReport(BaseModel):
    """
    Structured output schema for the BugFixer LLM response.
    Enforces clean JSON generation via grammar-constrained decoding (Pillar 1).
    """

    reasoning: str = Field(
        ...,
        description="Step-by-step Chain-of-Thought analysis of the error stack trace, inputs, and expected vs actual behavior."
    )
    root_cause: str = Field(
        ...,
        description="Precise summary of why the bug occurred (e.g., 'Off-by-one index error on empty list input')."
    )
    proposed_fix: str = Field(
        ...,
        description="High-level explanation of how the code was modified to resolve the root cause."
    )
    fixed_code: str = Field(
        ...,
        description="The complete, fixed Python code containing the full function or class definition. Do NOT wrap in markdown fences."
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Estimated confidence between 0.0 and 1.0 that this patch satisfies all unit tests."
    )

