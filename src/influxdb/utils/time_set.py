from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from enum import Enum
import re

PATTERN = r'^([+,-]?)(\d+)([s,m,h,d,y])'

class TimeZone(Enum):
    BEIJING = ZoneInfo('Asia/Shanghai')
    UTC = ZoneInfo('UTC')


        
def get_relative_time(r_time:str, tz: TimeZone = TimeZone.BEIJING):
    """
    根据相对时间字符串计算具体时间

    参数:
        r_time: 相对时间字符串, 格式如 +1h, -3d等,
                + 表示未来, - 表示过去, 默认+
                单位: s(秒), m(分), h(时), d(天), y(年)
        tz: 时区, 默认北京时间
    返回:
        计算后的具体时间(带时区信息)
    """

    result = re.match(PATTERN,r_time)
    if not result:
        raise ValueError(f"无效的相对时间格式: {r_time}, 请使用如`+1h`,`-3d`的格式")

    op, num, unit = result.groups()
    num = int(num)
    # 处理操作符, 默认是+
    if not op or op == '+':
        multipier = 1
    elif op == '-':
        multipier = -1
    else:
        raise ValueError(f"无效的操作符: {op}, 仅支持+ 或-")

    # 根据单位计算时间差
    now = datetime.now(tz.value)    #获取当前时区的时间
    unit_map = {
        's': timedelta(seconds=num * multipier),
        'm': timedelta(minutes=num * multipier),
        'h': timedelta(hours=num * multipier),
        'd': timedelta(days=num * multipier),
        'y': timedelta(days=num*365*multipier)
    }

    if unit not in unit_map:
        raise ValueError(f"无效的时间单位: {unit}, 仅支持: s, m, h, d, y")
    
    return now + unit_map[unit]


def is_relative_time(r_time: str):
    if re.match(PATTERN, r_time):
        return True
    return False