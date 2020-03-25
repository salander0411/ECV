# ECV
ECV python脚本

# Prerequisite 前置要求
**1.Linux 或 Windows上的Python 3 环境 , 安装 requests 和 boto3 库**
## Linux
`yum install python3`<br><br>
`pip3 install requests`<br><br>
`pip3 install boto3`<br><br>
## Windows
download python3 from [python.org](https://www.python.org/downloads/windows/)<br><br>
`pip3 install requests`<br><br>
`pip3 install boto3`<br><br>
**2.[Setup your credentials](https://docs.aws.amazon.com/zh_cn/cli/latest/userguide/cli-chap-configure.html) for AWS CLI，预先配置好AWS的密钥**


# Usage Guide 使用说明
## upload.py
功能：<br>
1.给定txt的链接文件，扫描链接并完成上传到s3的操作<br>
2.404的链接将不会上传文件，日志会被记录到同路径的404文件夹下的404.log日志文件中<br>
3.所有未成功的链接将记录到最新日期的log文件中（和upload.py脚本同一路径）<br>
<br>
自定义脚本参数（可以自行修改变量）：<br>
file_path = ''  - txt文件链接，字符串类型，例如 'btt1.txt'<br>
maxThreads = 300  - 线程数量，int类型，例如300<br>
bucket = 'test--20200310'  - s3桶名称，字符串类型<br>
prefix = 'video1-hsanhl-com/'   - s3桶前缀路径，字符串类型  最前面不要/,最后要/，比如 'abc/123/'<br>

## check_error.py
功能：<br>
1.检索·upload.py·生成的最新日期的日志，并自动上传所有被记录的失败链接<br>
2.404的链接将不会上传文件，日志会被记录到同路径的404文件夹下的404.log日志文件中<br>
3.所有未成功的链接将记录到最新日期的log文件中（和upload.py脚本同一路径）<br>
<br>
直接运行脚本即可<br>
可以通过修改 `upload.check_error(max_thread = 300)` 中的最大线程数来加快进度（受带宽和机器性能限制）<br>

## compare_ts.py
功能：<br>
1.给定txt文件，分析所有s3中ts文件数量，和链接中应有文件数量不相等的url，记录到同路径tsfile文件夹下的最新日期日志文件中<br>
自定义脚本参数（可以自行修改变量）：<br>
my_bucket = s3.Bucket('test--20200310')  - 修改s3桶名称<br>
txt_file = 'btt1.txt'   - txt文件路径<br>
prefix = ''   - 前缀名称，不修改则会根据链接自动检测<br>
<br>

## upload_again.py
功能：<br>
1.检索compare_ts.py生成的最新日期日志，并上传所有ts文件<br>
2.失败的链接会在同路径下的最新日期日志文件中<br>
<br>

## upload_index.py
功能：<br>
1.根据给定的txt文件，上传所有index.m3u8文件（同ts文件同一目录）<br>
2.bucket和prefix请在upload.py文件中指定
3.上传失败的链接会记录到同文件夹下的最新日期日志中
<br>
