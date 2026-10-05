import sys
import argparse
from pathlib import Path

# Fix Windows console UTF-8 encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


from src.agent import build_bugfixer_graph
from src.examples import CHALLENGES
from src.ui import print_banner, print_final_summary, console


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run the LangGraph BugFixer ReAct Loop"
    )
    parser.add_argument(
        "--challenge",
        choices=["1", "2", "3"],
        help="Challenge number to run (1: Palindrome, 2: Binary Search, 3: Flatten Dict)",
        default=None
    )
    parser.add_argument(
        "--code-file",
        type=str,
        help="Path to custom buggy Python code file",
        default=None
    )
    parser.add_argument(
        "--test-file",
        type=str,
        help="Path to custom unit test file",
        default=None
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum self-correction loop iterations (default: 5)"
    )
    return parser.parse_args()


def select_challenge_interactively() -> str:
    console.print("\n[bold cyan]Select a challenge to fix:[/bold cyan]")
    for key, c in CHALLENGES.items():
        console.print(f"  [bold yellow][{key}][/bold yellow] [bold white]{c['title']}[/bold white]")
        console.print(f"      [dim]{c['description']}[/dim]")
    
    choice = input("\nEnter choice [1-3] (default 1): ").strip() or "1"
    if choice not in CHALLENGES:
        choice = "1"
    return choice


def main():
    print_banner()
    args = parse_arguments()

    if args.code_file and args.test_file:
        task_desc = f"Custom task from {args.code_file}"
        code = Path(args.code_file).read_text(encoding="utf-8")
        test_code = Path(args.test_file).read_text(encoding="utf-8")
    else:
        choice = args.challenge or select_challenge_interactively()
        challenge_data = CHALLENGES[choice]
        task_desc = challenge_data["description"]
        code = challenge_data["buggy_code"]
        test_code = challenge_data["test_code"]
        console.print(f"\n[bold green]Selected:[/bold green] {challenge_data['title']}\n")

    initial_state = {
        "task_description": task_desc,
        "code": code,
        "test_code": test_code,
        "error_message": "",
        "iteration": 1,
        "max_iterations": args.max_iterations,
        "status": "running",
        "history": [],
        "last_report": None
    }

    graph = build_bugfixer_graph()

    # Run the graph
    final_state = graph.invoke(initial_state)

    print_final_summary(
        status=final_state["status"],
        total_iterations=final_state["iteration"] - 1 if final_state["status"] == "success" else final_state["iteration"],
        final_code=final_state["code"]
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Aborted by user.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
