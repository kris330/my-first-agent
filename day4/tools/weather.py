def get_weather(city: str) -> str:
    mock_data = {
        "北京": "晴，15°C，东风3级", "上海": "多云，18°C，南风2级",
        "广州": "小雨，22°C，偏东风", "深圳": "阴，24°C，东南风2级",
        "成都": "多云，16°C，微风",
    }
    return mock_data.get(city, f"{city}：晴，20°C（模拟数据）")
