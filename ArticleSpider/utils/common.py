#!/usr/bin/env python
#coding: utf-8
__author__ = 'lixl'
__date__ = '2018/8/9 23:04'
import hashlib

def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

if __name__ == '__main__':
    print(get_md5('http://jobbole.com/'.encode('utf8')))