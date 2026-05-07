def calculate(expression: str) -> str:
    allowed_chars = set("0123456789+-*/()., ")
    if not all(c in allowed_chars for c in expression):
        return f"表达式包含不允许的字符：{expression!r}"
    try:
        result = eval(expression)  # noqa: S307
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "错误：除数不能为零"
    except Exception as e:
        return f"计算出错：{e}"
