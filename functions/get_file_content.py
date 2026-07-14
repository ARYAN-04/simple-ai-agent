import os


def get_file_content(working_directory: str, file_path: str) -> str:
    resolved_wd = os.path.abspath(working_directory)
    resolved_target = os.path.abspath(os.path.join(working_directory, file_path))

    if not resolved_target.startswith(resolved_wd + os.sep):
        return f"Error: Cannot access '{file_path}' as it is outside the permitted working directory"

    if not os.path.isfile(resolved_target):
        return f"Error: File not found or is not a regular file: '{file_path}'"

    try:
        with open(resolved_target, "r", encoding="utf-8") as f:
            content = f.read()

        if len(content) > 10000:
            content = content[:10000]
            content += f'\n[...File "{file_path}" truncated at 10000 characters]'

        return content
    except Exception as e:
        return f"Error: {e}"
