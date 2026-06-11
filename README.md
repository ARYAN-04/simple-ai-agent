# simple-ai-agent

Minimal CLI chatbot powered by Google Gemini.

## Requirements

- Python 3.12+
- A Gemini API key

## Setup

```bash
echo 'GEMINI_API_KEY=your_key_here' > .env
uv sync          # or pip install -r requirements.txt
```

## Usage

```bash
python main.py "your prompt"
python main.py "your prompt" --verbose
```

### Dummy data

In `main.py`, uncomment the dummy data block at the top **and** the dummy block inside `main()`, then comment out the real API call block. Run normally — no flag needed.
