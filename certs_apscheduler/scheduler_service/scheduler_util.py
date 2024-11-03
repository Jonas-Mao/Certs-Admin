# -*- coding: utf-8 -*-


def crontab_compatible_weekday(expr):
    """
    # 0-6表示周日到周六，并支持7为周日

    map根据提供的函数对指定序列做映射：map(function, literation...)
    py2返回list，py3返回迭代器，需使用list转换
    def square(x):
        return x*x
    res = list(map(square, [1,2,3]))                        # [1,4,9]

    lambda匿名函数：lambda x,y,z...:表达式
    冒号前是参数，可以多个，冒号后为表达式。返回值是一个函数地址(函数对象)
    p = lambda x,y:x+y
    print(p(4,6))                                           # 10

    map(lambda x: x ** 2, [1, 2, 3, 4])                     # [1, 4, 9, 16]
    map(lambda x, y: x + y, [1, 3, 5, 7], [2, 4, 6, 8])     # [3, 7, 11, 15]
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
