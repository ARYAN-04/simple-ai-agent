from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file

FUNCTION_MAP = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(
    function_name: str,
    function_args: dict,
    working_directory: str,
    verbose: bool = False,
) -> str:
    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in FUNCTION_MAP:
        return f"Error: Unknown function: {function_name}"

    args = dict(function_args)
    args["working_directory"] = working_directory
    try:
        result = FUNCTION_MAP[function_name](**args)
    except TypeError as e:
        return f"Error: invalid arguments for {function_name}: {e}"
    return result
