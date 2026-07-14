def render(expression: str, result: float) -> str:
    line = "+" + "-" * (len(expression) + 4) + "+"
    return f"{line}\n| {expression} = {result} |\n{line}"
