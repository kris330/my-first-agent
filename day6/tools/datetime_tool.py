from datetime import datetime
import pytz


def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    try:
        tz = pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        tz = pytz.timezone("Asia/Shanghai")
        timezone = "Asia/Shanghai（时区名无效，已回退）"
    now = datetime.now(tz)
    return now.strftime(f"%Y年%m月%d日 %H:%M:%S（{timezone}）")
