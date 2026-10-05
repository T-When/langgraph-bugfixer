import sys
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

# Safe console configuration on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()


def print_banner():
    title = Text(">> LangGraph BugFixer -- Self-Correcting ReAct Agent", style="bold magenta")
    subtitle = Text("Pillar 1 & 2: Grammar-Constrained Outputs + Evaluator-Optimizer Cycle", style="italic cyan")
    console.print(Panel(Text.assemble(title, "\n", subtitle), border_style="magenta", expand=False))


def print_iteration_header(iteration: int, max_iterations: int):
    console.print(f"\n[bold yellow]=== Iteration {iteration} of {max_iterations} ===[/bold yellow]")


def print_test_results(passed: bool, output: str):
    if passed:
        panel = Panel(
            Text(f"[PASS] All unit tests PASSED successfully!\n\n{output}" if output else "[PASS] All unit tests PASSED successfully!", style="bold green"),
            title="[bold green]Test Runner[/bold green]",
            border_style="green",
        )
    else:
        # Trim traceback if too massive
        trimmed = output if len(output) < 1500 else output[:1500] + "\n...[truncated]"
        panel = Panel(
            Text(trimmed, style="bold red"),
            title="[bold red][FAIL] Tests Failed (Traceback / Error)[/bold red]",
            border_style="red",
        )
    console.print(panel)


def print_llm_fix_report(report: dict):
    reasoning = report.get("reasoning", "")
    root_cause = report.get("root_cause", "")
    proposed_fix = report.get("proposed_fix", "")
    confidence = report.get("confidence_score", 0.0)

    content = f"[bold cyan][Root Cause][/bold cyan] {root_cause}\n\n"
    content += f"[bold blue][Proposed Fix][/bold blue] {proposed_fix}\n\n"
    content += f"[bold magenta][CoT Reasoning][/bold magenta] {reasoning}\n\n"
    content += f"[bold yellow][Confidence Score][/bold yellow] {confidence * 100:.1f}%"

    console.print(Panel(content, title="[bold cyan]Agent Analysis & Plan[/bold cyan]", border_style="cyan"))


    code = report.get("fixed_code", "")
    if code:
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="[bold green]Generated Code Patch[/bold green]", border_style="green"))


def print_final_summary(status: str, total_iterations: int, final_code: str):
    table = Table(title="Execution Summary", border_style="cyan")
    table.add_column("Property", style="bold")
    table.add_column("Value", style="cyan")

    table.add_row("Outcome", f"[bold green]RESOLVED[/bold green]" if status == "success" else f"[bold red]FAILED[/bold red]")
    table.add_row("Total Iterations", str(total_iterations))

    console.print("\n")
    console.print(table)

    if status == "success":
        syntax = Syntax(final_code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="[bold green]Final Working Implementation[/bold green]", border_style="green"))
    else:
        console.print("[bold red]Failed to resolve bug within max iteration limits.[/bold red]")
