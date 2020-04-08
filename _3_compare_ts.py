#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 11:00:56 2020

@author: chenlaws

modified 2020-03-24
1. 增加index.m3u8后，ts文件夹内的s3总数量大1，即 get_s3_numbers = all_ts_numbers + 1
2. 不相等的子文件夹路径会输出到 not_equal_ts.log
3. 执行upload_again()函数即可遍历'not_equal_ts.log'，并完成上传（全部遍历一遍上传）
"""

import boto3
import requests
import logging
import _1_upload
import os
import time
import queue


def set_tslogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    if os.path.isdir('tsfile'):
        ch = logging.FileHandler('tsfile/%s.log'%time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
    else:
        os.mkdir('tsfile')
        ch = logging.FileHandler('tsfile/%s.log'%time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    return logger


def get_s3_numbers(bucket, prefix, path):
    return sum(1 for _ in bucket.objects.filter(Prefix=prefix+path))

def get_information(url):
    download = requests.get(url).text
    start    = download.find('000kb')-1
    newlink  = download[start:]
    new_url  = url[:url.find('index.m3u8')] + newlink
    
    prefix, path = get_prefix(new_url)
    
    all_ts_numbers = sum(1 for item in requests.get(new_url).text.split('\n') if len(item) > 0 and item[0] != '#')

    return all_ts_numbers, prefix, path

def get_prefix(new_url):
    '''
    根据url自动获得prefix + path
    '''
    #new_url='https://video1.hsanhl.com/20190607/Cf7c0NAe/1000kb/hls/index.m3u8'
    end_1 = new_url.find('/',10)
    end_2 = new_url.find(':',10)
    if end_1 >0 and end_2>0:
        end = min(end_1, end_2)
    else:
        end = max(end_1,end_2)
    prefix = new_url[new_url.find('//')+2:end].replace('.','-')+'/'    #'video1-hsanhl-com/'
    path = new_url[new_url.find('/',10)+1:new_url.find('index.m3u8')]  #20190607/Cf7c0NAe/
    return prefix, path


def upload_again(bucket, prefix, maxThreads = 300):
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
        path = os.getcwd()+'/tsfile'
        #获取所有log文件
        try:
            log_lists = filter(lambda x: '.log' in x,os.listdir(path))
        
            if not log_lists:
                print('no log files')
            log_file = get_latest_log(log_lists)
            print('lastest log file:',log_file)
        
            return 'tsfile/'+log_file
        except Exception as e:
            print(e)
    
    all_links_file = get_all_links()
    tslogger = set_tslogger()
        
    with open(all_links_file,'r') as f:
        all_m3u8_lists = f.read().splitlines()

    for url in all_m3u8_lists:
        _1_upload.multi_thread(url, maxThreads, tslogger, bucket, prefix)




def main():
    s3 = boto3.resource('s3')
    tslogger = set_tslogger()
    
    #自修改信息区域--------------------
    my_bucket = s3.Bucket('test--20200310')
    txt_file = 'btt1.txt'
    prefix = ''  # 最后需要带 "/", 如 "video-xxx-com/"
    #-------------------------------
    
    with open(txt_file) as f:
        for url in f.read().splitlines():
            all_ts_numbers, prefix_auto , path = get_information(url)
            if prefix == '':
                prefix = prefix_auto
            all_s3_ts_numbers = get_s3_numbers(my_bucket, prefix, path)
            if all_s3_ts_numbers-1 != all_ts_numbers:
                print('不相等,{0},s3:{1},should be:{2}'.format(url,all_s3_ts_numbers, all_ts_numbers))
                tslogger.error(url)
            else:
                print('yes,{0},numbers:{1}'.format(url, all_ts_numbers))

if __name__ == '__main__':
    main()
