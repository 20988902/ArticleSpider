#!/usr/bin/env python
#coding: utf-8
__author__ = 'lixl'
__date__ = '2018/8/8 22:00'

from scrapy.cmdline import execute
import sys,os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute(["scrapy", "crawl", "jobbole"])

