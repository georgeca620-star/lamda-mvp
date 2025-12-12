# backend/app/symbolic.py
from sympy import symbols, sympify, diff, integrate, simplify, latex
from sympy.parsing.sympy_parser import parse_expr
from typing import Dict, Any
import random

def parse_expression(expr_str: str):
    # Minimalistic parser: assumes valid math expression in plain text or latex-ish.
    try:
        expr = parse_expr(expr_str, evaluate=True)
        return expr
    except Exception as e:
        raise ValueError(f"Could not parse expression: {e}")

def differentiate(expr_str: str, var: str = 'x') -> Dict[str, Any]:
    x = symbols(var)
    expr = parse_expression(expr_str)
    deriv = diff(expr, x)
    return {
        "expression": str(expr),
        "derivative": str(simplify(deriv)),
        "latex_expression": latex(expr),
        "latex_derivative": latex(deriv)
    }

def integrate_expr(expr_str: str, var: str = 'x') -> Dict[str, Any]:
    x = symbols(var)
    expr = parse_expression(expr_str)
    integ = integrate(expr, x)
    return {
        "expression": str(expr),
        "integral": str(simplify(integ)),
        "latex_expression": latex(expr),
        "latex_integral": latex(integ)
    }

def simplify_expr(expr_str: str) -> Dict[str, Any]:
    expr = parse_expression(expr_str)
    simp = simplify(expr)
    return {
        "expression": str(expr),
        "simplified": str(simp),
        "latex_expression": latex(expr),
        "latex_simplified": latex(simp)
    }
