import sys
import tempfile
import subprocess
from pathlib import Path
from typing import Tuple


def run_code_against_tests(code: str, test_code: str, timeout_seconds: int = 6) -> Tuple[bool, str]:
    """
    Executes the candidate code concatenated with the unit test code in a temporary
    Python process with a strict timeout to prevent infinite loops.

    Returns:
        (passed: bool, output_or_error: str)
    """
    # Clean possible markdown ticks if any leaked
    cleaned_code = code.strip()
    if cleaned_code.startswith("```python"):
        cleaned_code = cleaned_code[9:]
    elif cleaned_code.startswith("```"):
        cleaned_code = cleaned_code[3:]
    if cleaned_code.endswith("```"):
        cleaned_code = cleaned_code[:-3]
    cleaned_code = cleaned_code.strip()

    full_script = f"""# --- CANDIDATE CODE ---
{cleaned_code}

# --- UNIT TESTS ---
{test_code}
"""

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(full_script)
        tmp_path = Path(tmp.name)

    try:
        proc = subprocess.run(
            [sys.executable, str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        if proc.returncode == 0:
            return True, proc.stdout.strip()
        else:
            err = proc.stderr.strip() or proc.stdout.strip()
            return False, err
    except subprocess.TimeoutExpired:
        return False, f"TimeoutExpired: Execution exceeded {timeout_seconds} seconds. Likely an infinite loop!"
    except Exception as e:
        return False, f"Execution failed: {str(e)}"
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass

