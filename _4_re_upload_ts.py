#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 14:59:45 2020

@author: chenlaws
"""

import _3_compare_ts

if __name__ == '__main__':
    maxThreads = 800
    bucket = 'test--20200310'
    prefix = 'video1-hsanhl-com/'   #最前面不要/,最后要/，比如 abc/123/
    
    _3_compare_ts.upload_again(bucket, prefix, maxThreads)

