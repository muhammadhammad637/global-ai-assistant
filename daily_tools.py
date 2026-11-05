"""Small offline tools that do not send user data to an external service."""

import ast
import math
import operator
from datetime import date


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_UNIT_FACTORS = {
    "length": {
        "meters": 1.0,
        "kilometers": 1000.0,
        "centimeters": 0.01,
        "miles": 1609.344,
        "feet": 0.3048,
        "inches": 0.0254,
    },
    "mass": {
        "grams": 1.0,
        "kilograms": 1000.0,
        "milligrams": 0.001,
        "pounds": 453.59237,
        "ounces": 28.349523125,
    },
    "volume": {
        "milliliters": 1.0,
        "liters": 1000.0,
        "cups_us": 236.5882365,
        "gallons_us": 3785.411784,
    },
}


def _evaluate_expression(node, depth=0):
    if depth > 20:
        raise ValueError("Calculator expression is too complex.")
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        value = node.value
    elif isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_expression(node.left, depth + 1)
        right = _evaluate_expression(node.right, depth + 1)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent must be between -100 and 100.")
        value = _BINARY_OPERATORS[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        value = _UNARY_OPERATORS[type(node.op)](
            _evaluate_expression(node.operand, depth + 1)
        )
    else:
        raise ValueError("Use numbers and +, -, *, /, //, %, **, and parentheses only.")

    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("The result must be a finite number.")
    if abs(value) > 1e100:
        raise ValueError("The result is too large.")
    return value


def calculate(expression):
    """Evaluate basic arithmetic without executing Python code."""
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("Enter a calculation first.")
    if len(expression) > 200:
        raise ValueError("Calculation must be 200 characters or fewer.")
    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ValueError("Enter a valid arithmetic expression.") from error
    if sum(1 for _ in ast.walk(parsed)) > 100:
        raise ValueError("Calculator expression is too complex.")
    try:
        return _evaluate_expression(parsed.body)
    except (ArithmeticError, OverflowError) as error:
        raise ValueError(f"Could not calculate this expression: {error}") from error


def available_units():
    return {
        **{dimension: tuple(units) for dimension, units in _UNIT_FACTORS.items()},
        "temperature": ("celsius", "fahrenheit", "kelvin"),
    }


def convert_units(value, source, target):
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Enter a finite numeric value.")
    for units in _UNIT_FACTORS.values():
        if source in units and target in units:
            converted = value * units[source] / units[target]
            return converted
    temperature_units = available_units()["temperature"]
    if source in temperature_units and target in temperature_units:
        if source == "celsius":
            celsius = value
        elif source == "fahrenheit":
            celsius = (value - 32) * 5 / 9
        else:
            celsius = value - 273.15
        if target == "celsius":
            return celsius
        if target == "fahrenheit":
            return celsius * 9 / 5 + 32
        return celsius + 273.15
    raise ValueError("Choose source and target units from the same category.")


def days_between(start, end):
    if not isinstance(start, date) or not isinstance(end, date):
        raise ValueError("Choose valid start and end dates.")
    return (end - start).days
