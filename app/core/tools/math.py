from langchain_core.tools import tool


@tool
def add(a: int, b: int) -> int:
    """两个数相加"""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """两个数相乘"""
    return a * b


@tool
def divide(a: int, b: int) -> float:
    """两个数相除"""
    if b == 0:
        return float("inf")
    return a / b