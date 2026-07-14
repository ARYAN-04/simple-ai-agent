import os


def write_file(working_directory: str, file_path: str, content: str) -> str:
    resolved_wd = os.path.abspath(working_directory)
    resolved_target = os.path.abspath(os.path.join(working_directory, file_path))

    if not resolved_target.startswith(resolved_wd + os.sep):
        return f"Error: Cannot access '{file_path}' as it is outside the permitted working directory"

    try:
        os.makedirs(os.path.dirname(resolved_target), exist_ok=True)
        with open(resolved_target, "w", encoding="utf-8") as f:
            f.write(content)
        return (
            f"Successfully wrote to '{file_path}' ({len(content)} characters written)"
        )
    except Exception as e:
        return f"Error: {e}"
