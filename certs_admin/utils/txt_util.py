# -*- coding: utf-8 -*-

import os


def read_txt(filename):
    """
    读取文本
    :param filename:
    """
    with open(filename, 'r') as f:
        for line in f.readlines():
            yield line.strip()


def write_txt(filename, rows):
    """
    写入到文本
    :param filename:
    :param rows:
    """
    with open(filename, 'w') as f:
        for row in rows:
            f.write(row + os.linesep)


if __name__ == '__main__':
    write_txt('demo.txt', ['1', '2'])

    for row in read_txt('demo.txt'):
        print(row)
