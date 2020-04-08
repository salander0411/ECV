#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 11:45:32 2020

@author: chenlaws
预安装库：requests, boto3
需要验证未成功上传的list的话，跑一遍 check_error()函数即可

modified 2020-03-24
1. 增加对1000kb/hls/index.m3u8 的上传
2. 404状态的文件不会上传，会记录链接给log文件
"""

import threading
import queue
import requests
import boto3
import logging
import time
import os

s3_client = boto3.client('s3')


class download_and_upload(threading.Thread):
    def __init__(self, link, queue, logger, bucket, prefix):
        threading.Thread.__init__(self)
        self.queue = queue
        self.link = link
        self.bucket = bucket
        self.path = prefix + link[link.find('/',10)+1:]
        self.logger = logger

    def run(self):
        try:
            #print('开始下载',self.path)
            file = requests.get(self.link)
            s3_client.put_object(Body=file.content, Bucket=self.bucket, Key=self.path)
        except Exception as e:
            print(e)
            self.logger.error(self.link)
        finally:
            self.queue.get(True,10)
            self.queue.task_done()

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    #if logger_name == '404logger' and not os.path.isdir('404'):
        #os.mkdir('404')
    fileHandler = logging.FileHandler(log_file, mode='w')
    streamHandler = logging.StreamHandler()

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)    

def get_all_ts_links(new_url):

    all_ts_names = requests.get(new_url).text.split('\n')
    pre = new_url[:new_url.find('index.m3u8')]
 
    all_ts_urls = (pre + i for i in filter(lambda x:len(x) > 0 and x[0] != '#',all_ts_names))
    return all_ts_urls

def multi_thread(url, maxThreads, logger, bucket, prefix):
    q = queue.Queue(maxThreads)
    print('dealing with:', url)
    
    download = requests.get(url).text
    start    = download.find('000kb') - 1
    newlink  = download[start:]
    new_url  = url[:url.find('index.m3u8')] + newlink  #'http://video2.youxijian.com:8091/20200305/40AEN3QJ/1000kb/hls/index.m3u8'
    
    t00 = download_and_upload(new_url, q, logger, bucket, prefix)
    t00.start()
    
    t0 = download_and_upload(url, q, logger, bucket, prefix)
    t0.start()
    
    jpg_link = url.replace('index.m3u8','1.jpg')
    t1 = download_and_upload(jpg_link, q, logger, bucket, prefix)
    t1.start()
    
    xml_link = url.replace('index.m3u8','index.xml')
    t2 = download_and_upload(xml_link, q, logger, bucket, prefix)
    t2.start()
    
    for ts_link in get_all_ts_links(new_url):
        q.put(ts_link)
        t = download_and_upload(ts_link, q, logger, bucket, prefix)
        t.start()
    q.join()
    #print('over')

def check_error(bucket, prefix, max_thread = 300):
    def get_latest_log(log_lists):
        latest_time = None
        for i in log_lists:
            time_ls = time.strptime(i[:-4],"%Y-%m-%d-%H-%M-%S")
            if latest_time == None:
                latest_time = time_ls
            elif time_ls > latest_time:
                latest_time = time_ls
        return time.strftime("%Y-%m-%d-%H-%M-%S", latest_time)+'.log'

    def get_all_links():
        path = os.getcwd()
        #获取所有log文件
        try:
            log_lists = filter(lambda x: '.log' in x,os.listdir(path))
        
            if not log_lists:
                print('no log files')
            log_file = get_latest_log(log_lists)
            print('lastest log file:',log_file)
        
            with open(log_file) as f:
                return [line.strip() for line in f.readlines()]
        except Exception as e:
            print(e)
    
    all_links = get_all_links()
    
    q = queue.Queue(max_thread)
    
    if all_links:
        setup_logger('log',r'%s.log'%time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
        logger = logging.getLogger('log')

        for link in all_links:
            #print(link)
            q.put(link)
            t = download_and_upload(link, q, logger, bucket, prefix)
            t.start()
        q.join()

def main():
    setup_logger('log',r'%s.log'%time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
    logger = logging.getLogger('log')

    with open(file_path,'r') as f:
        all_m3u8_lists = f.read().splitlines()

    #logging.info('main task starts')
    for url in all_m3u8_lists:
        multi_thread(url, maxThreads, logger, bucket, prefix)

if __name__ == '__main__':  
    #--------------------------------自修改信息区域------------------------------#
    
    file_path = 'btt1.txt'
    maxThreads = 300
    bucket = 'test--20200310'
    prefix = 'video1-hsanhl-com/'   #最前面不要/,最后要/，比如 abc/123/
    
    #--------------------------------------------------------------------------#

    main()
