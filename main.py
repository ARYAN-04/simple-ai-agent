import os
import sys
import time
import argparse
from types import SimpleNamespace as NS
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError

import config
from prompts import SYSTEM_PROMPT
from functions.call_function import call_function

_DUMMY_TEXT = "This is a simulated Gemini response for testing purposes."
_DUMMY_PROMPT_TOKENS = 42
_DUMMY_RESPONSE_TOKENS = 100

USE_REAL_API = True


def load_api_key() -> str:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        print("Error: GEMINI_API_KEY not found in environment or .env file")
        sys.exit(1)
    return api_key


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CLI agentic code editor")
    parser.add_argument("prompt", type=str, help="The task for the agent to perform")
    parser.add_argument("--verbose", action="store_true", help="Print agent internals")
    return parser.parse_args()


def build_tools() -> types.Tool:
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_files_info",
                description=(
                    "Lists files and subdirectories directly inside the given "
                    "directory (relative to the working directory), along with "
                    "their sizes and whether each is a directory."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "dir_path": {
                            "type": "string",
                            "description": (
                                "Directory to list, relative to the working "
                                "directory. Defaults to the working directory root."
                            ),
                        }
                    },
                    "required": [],
                },
            ),
            types.FunctionDeclaration(
                name="get_file_content",
                description="Reads and returns the text content of a file (truncated to 10000 characters if longer).",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file, relative to the working directory.",
                        }
                    },
                    "required": ["file_path"],
                },
            ),
            types.FunctionDeclaration(
                name="write_file",
                description="Overwrites (or creates) a file with the given content.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file, relative to the working directory.",
                        },
                        "content": {
                            "type": "string",
                            "description": "Full new content to write to the file.",
                        },
                    },
                    "required": ["file_path", "content"],
                },
            ),
            types.FunctionDeclaration(
                name="run_python_file",
                description="Executes a Python file with the `python` interpreter and returns its stdout, stderr, and exit code.",
                parameters={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the .py file, relative to the working directory.",
                        },
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional command-line arguments to pass to the script.",
                        },
                    },
                    "required": ["file_path"],
                },
            ),
        ]
    )


def build_config(tools: types.Tool) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[tools],
    )


def run_agentic_loop(api_key: str, user_prompt: str, verbose: bool) -> None:
    client = genai.Client(api_key=api_key)
    tool = build_tools()
    gen_config = build_config(tool)

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    for i in range(config.MAX_ITERS):
        if verbose:
            print(f"\n--- Iteration {i + 1} ---")

        # ===== REAL API CALL =====
        response = None
        if USE_REAL_API:
            for attempt in range(5):
                try:
                    response = client.models.generate_content(
                        model=config.MODEL_NAME,
                        contents=messages,
                        config=gen_config,
                    )
                    break
                except ClientError as e:
                    if e.code == 429 and attempt < 4:
                        wait = 2**attempt * 5
                        if verbose:
                            print(f"   Rate limited, retrying in {wait}s...")
                        time.sleep(wait)
                    else:
                        raise
        # ===== END REAL API CALL =====

        # ===== DUMMY API CALL (uncomment below, comment out real block above) =====
        # response = NS(
        #     text=_DUMMY_TEXT,
        #     usage_metadata=NS(
        #         prompt_token_count=_DUMMY_PROMPT_TOKENS,
        #         candidates_token_count=_DUMMY_RESPONSE_TOKENS,
        #     ),
        #     function_calls=[],
        #     candidates=[
        #         NS(
        #             content=NS(
        #                 parts=[NS(text=_DUMMY_TEXT, function_call=None)],
        #                 role="model",
        #             )
        #         )
        #     ],
        # )
        # ===== END DUMMY API CALL =====

        if response is None:
            print("Error: No response from API. Check your API key and quota.")
            return

        candidate = response.candidates[0] if response.candidates else None
        model_content = candidate.content if candidate else None

        if model_content:
            messages.append(model_content)

        function_calls = response.function_calls

        if not function_calls:
            if verbose and response.usage_metadata:
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(
                    f"Response tokens: {response.usage_metadata.candidates_token_count}"
                )
            if response.text:
                print(response.text)
            else:
                print("Agent finished (no final text response).")
            return

        for fc in function_calls:
            function_name = fc.name
            function_args = dict(fc.args) if fc.args else {}

            try:
                result = call_function(
                    function_name,
                    function_args,
                    working_directory=config.WORKING_DIR,
                    verbose=verbose,
                )
            except Exception as e:
                result = f"Error: unexpected exception during tool execution: {e}"

            if verbose:
                print(f"   -> {result[:200]}{'...' if len(result) > 200 else ''}")

            messages.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=function_name,
                                response={"result": result},
                                id=fc.id,
                            )
                        )
                    ],
                )
            )

    print(f"Max iterations ({config.MAX_ITERS}) reached without a final answer.")


def main() -> None:
    args = parse_args()
    api_key = load_api_key()
    run_agentic_loop(api_key, args.prompt, args.verbose)


if __name__ == "__main__":
    main()
