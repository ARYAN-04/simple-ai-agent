# simple-ai-agent

A CLI agentic code editor that uses Google Gemini to autonomously find and fix bugs in a codebase. The agent operates in a sandboxed calculator app, reading files, writing fixes, and running tests in a loop until the bug is resolved.

## How It Works

1. You provide a natural-language prompt (e.g. `"fix the bug in the calculator app"`)
2. The agent sends it to Gemini with four tool declarations: list files, read a file, write a file, run a Python file
3. Gemini calls tools in a loop, feeding results back, until it produces a final text answer
4. With `--verbose`, every tool call, its arguments, and its result are printed at each step

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- A [Gemini API key](https://aistudio.google.com/apikey)

## Setup

```bash
git clone <repo-url>
cd simple-ai-agent
cp .env.example .env      # add your API key
uv sync                    # install dependencies
```

## Usage

```bash
uv run main.py "the calculator gives the wrong answer for 3 + 5 * 2, please find and fix the bug, then verify with the tests" --verbose
```

### Without an API key (dummy mode)

In `main.py`, comment out the real API call block and uncomment the dummy block:

```python
# ===== REAL API CALL =====
# if USE_REAL_API:
#     ...
# ===== END REAL API CALL =====

# ===== DUMMY API CALL =====
response = NS(...)
# ===== END DUMMY API CALL =====
```

This lets you test the CLI argument parsing and program flow without spending API quota.

## Project Structure

```
simple-ai-agent/
├── main.py              # CLI entrypoint + agentic loop
├── config.py            # model name, working dir, max iterations
├── prompts.py           # system prompt for the LLM
├── functions/
│   ├── call_function.py       # dispatcher: maps tool name -> function
│   ├── get_files_info.py      # list files in a directory
│   ├── get_file_content.py    # read a file (truncated at 10k chars)
│   ├── write_file.py          # create/overwrite a file
│   └── run_python_file.py     # execute a .py file, return stdout/stderr
├── tests/
│   └── test_functions.py      # pytest unit tests for the tool functions
└── calculator/                # sandbox app the agent is allowed to modify
    ├── main.py
    ├── pkg/
    │   ├── calculator.py      # contains the intentional bug
    │   └── render.py
    └── tests.py               # tests the agent must make pass
```

## Testing

Run the tool function unit tests:

```bash
uv run pytest tests/ -v
```

Run the calculator sandbox tests (should fail before the agent runs):

```bash
uv run python calculator/tests.py
```

## Architecture Notes

- **Provider**: Uses the `google-genai` SDK (not `google-generativeai`). Tools go in `types.GenerateContentConfig(tools=[...])`, system instruction in `config.system_instruction`, function responses use `role="user"`.
- **Rate limiting**: Free tier Gemini has ~5 req/min. The agentic loop retries on 429 errors with exponential backoff.
- **Guardrails**: All tool functions resolve paths relative to `./calculator` and refuse to access files outside it.
- **Security**: `working_directory` is never exposed to the LLM. It is injected by `call_function.py` and hardcoded to `config.WORKING_DIR`.
