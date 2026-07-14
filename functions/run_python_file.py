import os
import subprocess


def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    resolved_wd = os.path.abspath(working_directory)
    resolved_target = os.path.abspath(os.path.join(working_directory, file_path))

    if not resolved_target.startswith(resolved_wd + os.sep):
        return f"Error: Cannot access '{file_path}' as it is outside the permitted working directory"

    if not os.path.exists(resolved_target):
        return f"Error: File '{file_path}' not found."

    if not resolved_target.endswith(".py"):
        return f"Error: '{file_path}' is not a Python file."

    try:
        result = subprocess.run(
            ["python", resolved_target] + (args or []),
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output_parts = []
        if result.stdout:
            output_parts.append(f"STDOUT: {result.stdout}")
        if result.stderr:
            output_parts.append(f"STDERR: {result.stderr}")

        if not output_parts:
            return "No output produced."

        output = "\n".join(output_parts)
        if result.returncode != 0:
            output += f"\nProcess exited with code {result.returncode}"
        return output

    except subprocess.TimeoutExpired:
        return "Error: process timed out after 30 seconds"
    except Exception as e:
        return f"Error: executing Python file: {e}"
