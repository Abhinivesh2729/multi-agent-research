"""Mock calculator tool for MCP server."""

import ast
import operator


CALCULATOR_TOOL = {
    "name": "calculator",
    "description": "Evaluate a basic arithmetic expression",
    "inputSchema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Arithmetic expression like '2 + 3 * 4'"
            }
        },
        "required": ["expression"]
    }
}


_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> float:
    """Safely evaluate supported arithmetic AST nodes."""
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _BINARY_OPS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        operand = _eval_node(node.operand)
        return _UNARY_OPS[type(node.op)](operand)

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    raise ValueError("Unsupported expression")


async def handle_calculation(expression: str) -> str:
    """Evaluate a math expression and return a readable result string."""
    try:
        parsed = ast.parse(expression, mode="eval")
        result = _eval_node(parsed.body)
    except ZeroDivisionError:
        return "Calculation error: division by zero"
    except Exception:
        return "Calculation error: invalid expression"

    # Return int-like numbers without trailing .0 for cleaner output.
    if result.is_integer():
        return str(int(result))
    return str(result)