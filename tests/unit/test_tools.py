"""Tests for tool implementations."""

from agentic_ai.tools.calculator import calculator
from agentic_ai.tools.web_search import web_search


class TestCalculator:
    def test_basic_addition(self) -> None:
        assert calculator.invoke("2 + 3") == "5.0"

    def test_multiplication(self) -> None:
        assert calculator.invoke("42 * 17") == "714.0"

    def test_complex_expression(self) -> None:
        assert calculator.invoke("(3 + 5) ** 2") == "64.0"

    def test_division(self) -> None:
        assert calculator.invoke("10 / 3") == str(10 / 3)

    def test_negative_numbers(self) -> None:
        assert calculator.invoke("-5 + 3") == "-2.0"

    def test_division_by_zero(self) -> None:
        result = calculator.invoke("1 / 0")
        assert "Error" in result

    def test_invalid_expression(self) -> None:
        result = calculator.invoke("import os")
        assert "Error" in result

    def test_no_function_calls(self) -> None:
        result = calculator.invoke("__import__('os').system('ls')")
        assert "Error" in result


class TestWebSearch:
    def test_returns_stub(self) -> None:
        result = web_search.invoke("test query")
        assert "stub" in result.lower()
        assert "test query" in result
