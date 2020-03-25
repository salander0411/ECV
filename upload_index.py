#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 23:09:07 2020

@author: chenlaws
"""

import upload

file_path = 'btt1.txt'
maxThreads = 300


with open(file_path,'r') as f:
    all_m3u8_lists = f.read().splitlines()

logger = upload.set_logger()
logger_404 = upload.set_404logger()

q = upload.queue.Queue(maxThreads)

for url in all_m3u8_lists:
    download = upload.requests.get(url).text
    start    = download.find('000kb') - 1
    newlink  = download[start:]
    new_url  = url[:url.find('index.m3u8')] + newlink  #'http://video2.youxijian.com:8091/20200305/40AEN3QJ/1000kb/hls/index.m3u8'
    
    q.put(new_url)
    task = upload.download_and_upload(new_url, q, logger, logger_404)
    task.start()

q.join()