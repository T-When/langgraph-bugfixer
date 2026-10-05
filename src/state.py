from typing import TypedDict, List, Dict, Any, Optional


class BugFixerState(TypedDict):
    """
    Central state machine schema for the LangGraph BugFixer loop.
    Passed between the evaluator, reasoning agent, and executor nodes.
    """

    task_description: str
    code: str
    test_code: str
    error_message: str
    iteration: int
    max_iterations: int
    status: str  # "running" | "success" | "failed"
    history: List[Dict[str, Any]]
    last_report: Optional[Dict[str, Any]]

