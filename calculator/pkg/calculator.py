import re


class Calculator:
    def evaluate(self, expression: str) -> float:
        tokens = self._tokenize(expression)
        return self._evaluate_tokens(tokens)

    def _tokenize(self, expression: str) -> list[str]:
        tokens = re.findall(r"\d+\.?\d*|[+\-*/()]", expression)
        return tokens

    def _evaluate_tokens(self, tokens: list[str]) -> float:
        result = 0.0
        operator = "+"
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token in "+-":
                operator = token
            elif token in "*/":
                pass
            elif token == "(":
                sub_expr = []
                depth = 1
                i += 1
                while i < len(tokens) and depth > 0:
                    if tokens[i] == "(":
                        depth += 1
                    elif tokens[i] == ")":
                        depth -= 1
                    if depth > 0:
                        sub_expr.append(tokens[i])
                    i += 1
                value = self._evaluate_tokens(sub_expr)
                result = self._apply_operator(result, value, operator)
            else:
                value = float(token)
                result = self._apply_operator(result, value, operator)
            i += 1
        return result

    def _apply_operator(self, left: float, right: float, operator: str) -> float:
        if operator == "+":
            return left + right
        elif operator == "-":
            return left - right
        elif operator == "*":
            return left * right
        elif operator == "/":
            return left / right
        return right
