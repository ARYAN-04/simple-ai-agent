import os
import sys
import argparse
from types import SimpleNamespace as NS
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Dummy Data
_DUMMY_TEXT = "This is a simulated Gemini response for testing purposes."
_DUMMY_PROMPT_TOKENS = 42
_DUMMY_RESPONSE_TOKENS = 100

def load_api_key() -> str:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        print("get the api key figured out")
        sys.exit(1)
    return api_key


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()


def build_messages(prompt: str) -> list[types.Content]:
    return [types.Content(role="user", parts=[types.Part(text=prompt)])]


def call_gemini(
    api_key: str, messages: list[types.Content]
) -> types.GenerateContentResponse:
    client = genai.Client(api_key=api_key)
    return client.models.generate_content(model="gemini-2.5-flash", contents=messages)


def display_response(response, args: argparse.Namespace) -> None:
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

        if response.usage_metadata is not None:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        else:
            print("no metadata")

    print(f"Response: {response.text}")


def main() -> None:
    api_key = load_api_key()
    args = parse_args()
    messages = build_messages(args.user_prompt)

    # ===== REAL API CALL (uncomment this block, comment out the dummy block below) ====
    # response = call_gemini(api_key, messages)
    # ================================================================================

    # ===== DUMMY API CALL (uncomment this block, comment out the real block above) ====
    response = NS(
        text=_DUMMY_TEXT,
        usage_metadata=NS(
            prompt_token_count=_DUMMY_PROMPT_TOKENS,
            candidates_token_count=_DUMMY_RESPONSE_TOKENS,
        ),
    )
    # ================================================================================

    display_response(response, args)


if __name__ == "__main__":
    main()