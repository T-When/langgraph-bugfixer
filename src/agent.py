import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from src.state import BugFixerState
from src.models import CodeFixReport
from src.executor import run_code_against_tests
from src.ui import (
    print_iteration_header,
    print_test_results,
    print_llm_fix_report,
    console
)

load_dotenv()


def get_llm():
    # Check all common environment variable names for the Gemini API key
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_GEMINI_KEY_1")
        or os.getenv("GOOGLE_GEMINI_KEY")
    )
    if not api_key:
        raise ValueError(
            "No Gemini API key found! Please set GEMINI_API_KEY in your .env file or environment."
        )

    model_name = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
    
    # Initialize LangChain Google GenAI client
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.2,
        max_retries=2,
    )
    # Enforce Structured Output via Pydantic schema (Pillar 1)
    return llm.with_structured_output(CodeFixReport)


def invoke_llm_with_retry(structured_llm, prompt: str, max_retries: int = 4) -> CodeFixReport:
    """
    Invokes the Gemini model with smart cooldown handling for the free tier quota (429/503).
    """
    import re

    for attempt in range(max_retries):
        try:
            return structured_llm.invoke(prompt)
        except Exception as e:
            err_msg = str(e)
            if ("429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "503" in err_msg) and attempt < max_retries - 1:
                # Check for explicit retry delay in response (e.g. 'retry in 45s' or 'retryDelay: 45s')
                delay = 15.0
                match = re.search(r'retry.*?(\d+(?:\.\d+)?)s', err_msg, re.IGNORECASE)
                if match:
                    delay = float(match.group(1)) + 2.0
                else:
                    delay = (attempt + 1) * 12.0

                console.print(
                    f"\n[bold yellow]Free-tier quota limit reached. Pausing for {delay:.1f}s before retrying (attempt {attempt+1}/{max_retries})...[/bold yellow]"
                )
                time.sleep(delay)
            else:
                raise e



def test_runner_node(state: BugFixerState) -> dict:
    """
    Executes the current code candidate against the unit tests.
    """
    print_iteration_header(state["iteration"], state["max_iterations"])
    with console.status("[bold green]Executing tests in subprocess sandbox...[/bold green]"):
        passed, output = run_code_against_tests(state["code"], state["test_code"])

    print_test_results(passed, output)

    if passed:
        return {
            "error_message": "",
            "status": "success"
        }
    else:
        return {
            "error_message": output,
            "status": "running"
        }


def route_decision(state: BugFixerState) -> str:
    """
    Conditional router deciding whether to terminate or continue the loop.
    """
    if state["status"] == "success":
        return END
    if state["iteration"] >= state["max_iterations"]:
        return END
    return "fix_generator"


def fix_generator_node(state: BugFixerState) -> dict:
    """
    Agentic reasoning node: inspects error output and history,
    reasons about the root cause, and generates a structured code fix.
    """
    structured_llm = get_llm()

    # Build prompt with history (Episodic Reflection)
    history_text = ""
    if state.get("history"):
        history_text = "\n### PREVIOUS FAILED ATTEMPTS AND FIXES:\n"
        for idx, entry in enumerate(state["history"]):
            history_text += f"- Attempt #{idx+1}: Root Cause '{entry.get('root_cause')}' -> Fix '{entry.get('proposed_fix')}'\n"

    system_prompt = f"""You are an elite automated Python software debugger.
Your goal is to fix the buggy Python code so that it passes ALL specified unit tests.

### TASK SPECIFICATION:
{state['task_description']}

### CURRENT CODE:
```python
{state['code']}
```

### UNIT TESTS TO PASS:
```python
{state['test_code']}
```

### RECENT EXECUTION ERROR / TRACEBACK:
{state['error_message']}
{history_text}

### INSTRUCTIONS:
1. Carefully analyze the traceback and unit test assertions.
2. Formulate step-by-step reasoning explaining the root cause.
3. Fix the bug while preserving any existing correct functionality.
4. Output the complete, runnable Python code with all necessary imports.
5. Provide your structured analysis adhering strictly to the schema.
"""

    with console.status("[bold cyan]Gemini is analyzing traceback and synthesizing fix...[/bold cyan]"):
        report: CodeFixReport = invoke_llm_with_retry(structured_llm, system_prompt)

    report_dict = report.model_dump()
    print_llm_fix_report(report_dict)

    # Record attempt into episodic history
    new_history = list(state.get("history", []))
    new_history.append({
        "iteration": state["iteration"],
        "root_cause": report.root_cause,
        "proposed_fix": report.proposed_fix,
        "error_encountered": state["error_message"]
    })

    return {
        "code": report.fixed_code,
        "iteration": state["iteration"] + 1,
        "history": new_history,
        "last_report": report_dict
    }


def build_bugfixer_graph():
    """
    Constructs the LangGraph StateGraph.
    """
    workflow = StateGraph(BugFixerState)

    # Add nodes
    workflow.add_node("test_runner", test_runner_node)
    workflow.add_node("fix_generator", fix_generator_node)

    # Entry point
    workflow.set_entry_point("test_runner")

    # Conditional branching
    workflow.add_conditional_edges(
        "test_runner",
        route_decision,
        {
            END: END,
            "fix_generator": "fix_generator"
        }
    )

    # Edge from fix_generator back to test_runner (Loop)
    workflow.add_edge("fix_generator", "test_runner")

    return workflow.compile()
