# coding=utf-8
import sys
import os


def progress(count):
    sys.stdout.write("\r" + "=" * count + "》" + f"{count}%")


def mkdir(path):
    if os.path.exists(path) is False:
        os.mkdir(path)
