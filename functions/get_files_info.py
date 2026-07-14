import os


def get_files_info(working_directory: str, dir_path: str = ".") -> str:
    resolved_wd = os.path.abspath(working_directory)
    resolved_target = os.path.abspath(os.path.join(working_directory, dir_path))

    if (
        not resolved_target.startswith(resolved_wd + os.sep)
        and resolved_target != resolved_wd
    ):
        return f"Error: Cannot access '{dir_path}' as it is outside the permitted working directory"

    if not os.path.isdir(resolved_target):
        return f"Error: '{dir_path}' is not a directory"

    try:
        entries = []
        for name in sorted(os.listdir(resolved_target)):
            full_path = os.path.join(resolved_target, name)
            size = os.path.getsize(full_path)
            is_dir = os.path.isdir(full_path)
            entries.append(f" - {name}: file_size={size}, is_dir={is_dir}")
        return (
            f"Result for {dir_path}:\n" + "\n".join(entries)
            if entries
            else f"Result for {dir_path}:\n (empty directory)"
        )
    except OSError as e:
        return f"Error: {e}"
