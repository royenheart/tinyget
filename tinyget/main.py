#!/usr/bin/env python3
from .wrappers import PackageManager
import sys


def cli():
    print(sys.argv)
    print(PackageManager)
