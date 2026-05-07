import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> None:
    """加载 .env 文件，检查必要配置是否存在。"""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        # 向上找一级（开发时从项目根目录运行）
        env_path = Path(__file__).parent.parent / ".env"

    load_dotenv(dotenv_path=env_path)

    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError(
            "\n错误：缺少 OPENAI_API_KEY\n"
            "\n解决方法：\n"
            "  1. 在项目根目录找到 .env.example 文件\n"
            "  2. 复制一份：cp .env.example .env\n"
            "  3. 用文本编辑器打开 .env，填入你的 API Key\n"
            "  4. 重新运行\n"
        )


def get_model() -> str:
    """返回要使用的模型名，可通过环境变量覆盖。"""
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def get_base_url() -> str | None:
    """返回自定义 base_url（国内 API 用），没设置则返回 None。"""
    return os.environ.get("OPENAI_BASE_URL") or None
