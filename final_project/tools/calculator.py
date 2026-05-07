def calculate(expression: str) -> str:
    """计算数学表达式，只允许数字和基本运算符。"""
    allowed_chars = set("0123456789+-*/()., ")
    if not all(c in allowed_chars for c in expression):
        return f"表达式包含不允许的字符，拒绝计算：{expression!r}"
    try:
        result = eval(expression)  # noqa: S307
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "错误：除数不能为零"
    except SyntaxError:
        return f"表达式语法错误：{expression!r}"
    except Exception as e:
        return f"计算出错：{e}"
