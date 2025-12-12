# backend/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from symbolic import differentiate, integrate_expr, simplify_expr, parse_expression
from llm_adapter import call_llm
from verification import numeric_check
from viz import plot_function, animate_transform
import asyncio

app = FastAPI(title="LAMDA MVP API", version="0.1.0")

class Query(BaseModel):
    natural: str
    action: Optional[str] = "auto"  # "differentiate", "integrate", "simplify", "plot"
    var: Optional[str] = "x"

@app.post("/api/solve")
async def solve(q: Query):
    """
    Endpoint to accept natural-language math query and return symbolic + verification + visual artifacts.
    """
    # 1) Ask LLM to canonicalize into a symbolic expression (if available).
    prompt = f"Convert this into a canonical sympy expression: {q.natural}"
    llm_resp = await call_llm(prompt)
    # Heuristic: try to extract something in backticks or last line; fall back to user text
    # Simple cleaning for this prototype:
    candidate = None
    try:
        # naive extraction
        import re
        m = re.search(r"`([^`]+)`", llm_resp)
        candidate = m.group(1) if m else llm_resp.strip().splitlines()[-1]
        # if still long, use original natural as fallback
        if len(candidate) > 400:
            candidate = q.natural
    except Exception:
        candidate = q.natural

    # 2) Route to symbolic engine
    try:
        if q.action == "differentiate":
            sym_res = differentiate(candidate, var=q.var)
        elif q.action == "integrate":
            sym_res = integrate_expr(candidate, var=q.var)
        elif q.action == "simplify":
            sym_res = simplify_expr(candidate)
        elif q.action == "plot" or q.action == "auto":
            # default to try differentiation if phrase contains 'derivative' else plot
            if "derivative" in q.natural.lower() or "differentiate" in q.natural.lower():
                sym_res = differentiate(candidate, var=q.var)
            else:
                # build a plot
                pic = plot_function(candidate)
                sym_res = {"expression": candidate, "plot": pic["path"]}
        else:
            sym_res = {"expression": candidate}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Symbolic error: {e}")

    # 3) Try verification when appropriate
    verification = {"ok": None}
    if "derivative" in sym_res.get("latex_expression", "") or "derivative" in q.action:
        # trivial example: verify derivative by numeric check
        # For prototype, check derivative by numeric difference of derivative and sympy computed
        # Skip heavy checks here.
        verification = {"note": "verification not implemented in detail in prototype"}

    return {
        "llm_raw": llm_resp,
        "canonical": candidate,
        "symbolic": sym_res,
        "verification": verification
    }

@app.post("/api/animate")
async def animate(q: Query):
    try:
        out = animate_transform(q.natural)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
