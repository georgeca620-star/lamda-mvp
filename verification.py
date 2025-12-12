# backend/app/verification.py
import numpy as np
from sympy import lambdify
from typing import Dict, Any
import random

def numeric_check(expr_str: str, candidate_str: str, var: str = 'x', samples: int = 6) -> Dict[str, Any]:
    """
    Performs numeric testing of equality between two expressions on random sample points.
    """
    try:
        # lazy import to avoid overhead if not used
        from sympy.parsing.sympy_parser import parse_expr
        from sympy import symbols
        x = symbols(var)
        e1 = parse_expr(expr_str)
        e2 = parse_expr(candidate_str)
        f1 = lambdify(x, e1, modules=['numpy'])
        f2 = lambdify(x, e2, modules=['numpy'])
        xs = np.linspace(-5, 5, samples)
        diffs = []
        for xv in xs:
            try:
                v1 = f1(xv)
                v2 = f2(xv)
                diffs.append(float(np.nan_to_num(v1 - v2)))
            except Exception:
                diffs.append(float('nan'))
        ok = all(np.isfinite(d) and abs(d) < 1e-6 for d in diffs)
        return {"ok": ok, "samples": xs.tolist(), "diffs": [float(d) for d in diffs]}
    except Exception as e:
        return {"ok": False, "error": str(e)}
