"""Tools for web search, safe arithmetic, and sandboxed local file reading."""
from __future__ import annotations

import ast
import math
import operator
from pathlib import Path
from typing import Any

from ddgs import DDGS
from langchain_core.tools import tool

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = (PROJECT_DIR / "data").resolve()
DATA_DIR.mkdir(exist_ok=True)

# Explicit allowlist: never use eval() for user-supplied expressions.
_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "abs": abs,
    "round": round,
}
_CONSTANTS = {"pi": math.pi, "e": math.e}
_MAX_POWER = 100
_MAX_ABS_VALUE = 1e100


def safe_calculate(expression: str) -> float | int:
    """Evaluate a restricted arithmetic expression without eval/exec."""
    if len(expression) > 300:
        raise ValueError("Expression is too long.")
    try:
        root = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Invalid mathematical expression.") from exc

    def visit(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            value = node.value
        elif isinstance(node, ast.Name) and node.id in _CONSTANTS:
            value = _CONSTANTS[node.id]
        elif isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > _MAX_POWER:
                raise ValueError("Exponent magnitude is too large.")
            value = _BINARY_OPERATORS[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
            value = _UNARY_OPERATORS[type(node.op)](visit(node.operand))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCTIONS:
            if node.keywords:
                raise ValueError("Keyword arguments are not supported.")
            value = _FUNCTIONS[node.func.id](*(visit(arg) for arg in node.args))
        else:
            raise ValueError(f"Unsupported expression element: {type(node).__name__}")
        if isinstance(value, (int, float)) and (not math.isfinite(value) or abs(value) > _MAX_ABS_VALUE):
            raise ValueError("Result is outside the supported numeric range.")
        return value

    try:
        return visit(root)
    except (ZeroDivisionError, OverflowError) as exc:
        raise ValueError(str(exc)) from exc


@tool
def web_search_tool(query: str) -> str:
    """Search the web with DuckDuckGo. Input a focused search query; returns titles, snippets, and URLs."""
    if not query.strip():
        return "Search query cannot be empty."
    try:
        results = list(DDGS().text(query, max_results=5))
    except Exception as exc:
        return f"DuckDuckGo search failed: {type(exc).__name__}: {exc}"
    if not results:
        return "No results found. Try a more specific search query."
    lines = []
    for i, item in enumerate(results, 1):
        title = item.get("title", "Untitled")
        body = item.get("body", item.get("snippet", ""))
        url = item.get("href", item.get("url", ""))
        lines.append(f"{i}. {title}\n   Summary: {body}\n   URL: {url}")
    return "\n".join(lines)


@tool
def calculator_tool(expression: str) -> str:
    """Calculate arithmetic safely. Supports +, -, *, /, //, %, **, parentheses, pi, e, and functions sqrt, sin, cos, tan, log, log10, abs, round."""
    try:
        result = safe_calculate(expression)
        return f"{expression} = {result}"
    except Exception as exc:
        return f"Calculation error: {exc}"


@tool
def file_reader_tool(filename: str) -> str:
    """Read a UTF-8 text, Markdown, CSV, or JSON file located inside the project's data/ directory. Input a filename such as notes.txt, not an absolute path."""
    try:
        requested = Path(filename)
        if requested.is_absolute():
            return "Access denied: provide a filename relative to the data directory."
        target = (DATA_DIR / requested).resolve()
        if target != DATA_DIR and DATA_DIR not in target.parents:
            return "Access denied: path must stay inside the data directory."
        if not target.is_file():
            available = sorted(p.name for p in DATA_DIR.iterdir() if p.is_file())
            return f"File not found: {filename}. Available files: {available or '(none yet)'}"
        if target.suffix.lower() not in {".txt", ".md", ".csv", ".json", ".log"}:
            return "Unsupported file type. Allowed: .txt, .md, .csv, .json, .log"
        if target.stat().st_size > 1_000_000:
            return "File is larger than the 1 MB limit."
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "Could not read file: expected UTF-8 text."
    except OSError as exc:
        return f"File read error: {exc}"
