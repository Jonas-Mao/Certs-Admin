# -*- coding: utf-8 -*-


def crontab_compatible_weekday(expr):
    """
    # 0-6表示周日到周六，并支持7为周日
    """
    if expr == "*":
        return expr

    mapping = {
        "0": "sun",
        "1": "mon",
        "2": "tue",
        "3": "wed",
        "4": "thu",
        "5": "fri",
        "6": "sat",
        "7": "sun"
    }

    return "".join(map(lambda x: mapping.get(x), expr))
