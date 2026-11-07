
import pytest

import tools
from tools import safe_calculate


# -----------------------------
# Calculator tests
# -----------------------------

def test_basic_arithmetic():
    assert safe_calculate("2 + 3 * 4") == 14
    assert safe_calculate("(10 - 4) / 2") == 3
    assert safe_calculate("sqrt(81)") == 9
    assert safe_calculate("2 ** 3") == 8
    assert safe_calculate("pi * 2") == pytest.approx(6.283185307)


def test_rejects_code_execution():
    with pytest.raises(ValueError):
        safe_calculate("__import__('os').system('echo unsafe')")

    with pytest.raises(ValueError):
        safe_calculate("[1, 2, 3]")

    with pytest.raises(ValueError):
        safe_calculate("2 ** 999")


def test_division_by_zero():
    with pytest.raises(ValueError):
        safe_calculate("1 / 0")


def test_invalid_math_functions():
    with pytest.raises(ValueError):
        safe_calculate("sqrt(-1)")

    with pytest.raises(ValueError):
        safe_calculate("unknown_function(10)")


def test_calculator_tool_handles_invalid_arguments():
    result = tools.calculator_tool.invoke({"expression": "sqrt()"})

    assert "Calculation error:" in result


def test_calculator_rejects_boolean_values():
    with pytest.raises(ValueError):
        safe_calculate("True + 1")


def test_calculator_rejects_long_expressions():
    with pytest.raises(ValueError):
        safe_calculate("1" * 301)


# -----------------------------
# File reader tests
# -----------------------------

def test_file_reader_reads_data_file(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "DATA_DIR", tmp_path)

    fixture = tmp_path / "sample.txt"
    fixture.write_text("hello agent", encoding="utf-8")

    result = tools.file_reader_tool.invoke({"filename": "sample.txt"})

    assert "hello agent" in result


def test_file_reader_handles_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "DATA_DIR", tmp_path)

    result = tools.file_reader_tool.invoke(
        {"filename": "missing.txt"}
    )

    assert "File not found" in result


def test_file_reader_blocks_parent_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "DATA_DIR", tmp_path)

    result = tools.file_reader_tool.invoke(
        {"filename": "../README.md"}
    )

    assert "Access denied" in result


def test_file_reader_blocks_absolute_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "DATA_DIR", tmp_path)

    outside_file = tmp_path.parent / "outside.txt"

    result = tools.file_reader_tool.invoke(
        {"filename": str(outside_file.resolve())}
    )

    assert "Access denied" in result


def test_file_reader_rejects_unsupported_extensions(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "DATA_DIR", tmp_path)

    fixture = tmp_path / "program.exe"
    fixture.write_text("not allowed", encoding="utf-8")

    result = tools.file_reader_tool.invoke(
        {"filename": "program.exe"}
    )

    assert "Unsupported file type" in result


def test_file_reader_rejects_oversized_files(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "DATA_DIR", tmp_path)

    fixture = tmp_path / "large.txt"
    fixture.write_text("a" * 1_000_001, encoding="utf-8")

    result = tools.file_reader_tool.invoke(
        {"filename": "large.txt"}
    )

    assert "1 MB limit" in result


# -----------------------------
# Web search tests
# -----------------------------

def test_web_search_rejects_empty_query():
    result = tools.web_search_tool.invoke({"query": "   "})

    assert "cannot be empty" in result


def test_web_search_handles_provider_failure(monkeypatch):
    class FailingDDGS:
        def text(self, query, max_results):
            raise ConnectionError("Simulated connection failure")

    monkeypatch.setattr(tools, "DDGS", FailingDDGS)

    result = tools.web_search_tool.invoke(
        {"query": "Python official downloads"}
    )

    assert "DuckDuckGo search failed" in result
    assert "ConnectionError" in result
