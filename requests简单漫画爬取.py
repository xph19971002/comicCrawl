# -*- coding: utf-8 -*-
__author__ = 'xi'
__date__ = '2019/1/4 9:28'
import re
import time
import random
import requests

'''   User-Agent 代理池   '''

ua_pool_list = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1',
    'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3',
]

'''   IP代理池   '''

proxy_pool_list = [
    '188.168.75.254:56899',
    '51.255.28.62:53281',
    '182.253.6.234:8080',
    '213.187.118.184:53281',
    '185.118.26.10:80',
    '50.201.51.216:8080',
    '109.87.30.193:21776',
    '5.135.164.72:3128',
    '79.111.13.155:50625',
]

'''   随机生成UA和IP   '''

UA = random.choice(ua_pool_list)
PROXY = random.choice(proxy_pool_list)

headers = {
    'User-Agent': UA
}
proxies = {
    'proxies': PROXY
}

'''   获取每一话的url   '''

# 此处url为选中某漫画后的首页，页面可以选择看哪一话
url = 'http://comic2.kukudm.com/comiclist/2247/index.htm'
# 获取页面
r = requests.get(url=url, headers=headers, proxies=proxies)
# 页面解码
c = r.content.decode('gbk')
# 使用正则初步筛选出所有包含每话url信息的html代码部分 类型为列表
inc_url_contents = re.findall('<dd>.*?<a.*?>.*?</a>.*?</dd>', c, re.S)
# print(first_result)

# 遍历上述列表 得到单一包含url信息的html代码块 类型为字符串
num = 1
for inc_url_content in inc_url_contents:
    # print(url_content)

    # 使用正则 将带有url地址和章节名的信息筛选出来 类型为列表套元组  [('2247/54297/1.htm', '在魔王城说晚安 1话')]
    part_url_tup = re.findall("<A.*?href='/comiclist/(.*?)'.*?>(.*?)</A>", inc_url_content)[0]
    # 分析页面 将路径重新拼接 该路径为每话的真实路径
    url = 'http://comic2.kukudm.com/comiclist/' + part_url_tup[0]

    '''   获取每一话有多少张图片   '''

    # 获取每一话的页面信息，找出每话有多少张图片
    r = requests.get(url=url, headers=headers, proxies=proxies)
    # 页面解码
    c = r.content.decode('gbk')
    # 使用正则找出包含每话张数信息的html代码块 类型为列表
    fourth_result = re.findall("<td.*?valign='top'.*?>(.*?)<", c, re.S)[0]
    # print(fourth_result)
    # 进一步使用正则筛选出页码
    page_num = re.findall('共(.*?)页', fourth_result)[0]

    # print(f"{url}：{part_url_tup[1]},该话有{page_num}页")

    '''   获取每一话的每一张图片并下载  '''

    # 每个章节的章节号码
    chapter_num = re.findall('\d{5}', url)[0]
    for page in range(1, int(page_num) + 1):
        # 获取每一话的页面
        r = requests.get(f'http://comic2.kukudm.com/comiclist/2247/{chapter_num}/{page}.htm', headers=headers,
                         proxies=proxies)
        # print(r.status_code)
        # 因图片为二进制 故获取二进制内容
        c = r.content
        # 第一次正则匹配 匹配包含图片信息的html代码块 类型为字符串
        inc_img_str = re.search(b'<img(.*?)src="(.*?)">', c, re.S)
        # 解码
        img_str = inc_img_str.group(1).decode('gbk')
        # print(str1)
        # 第二次正则匹配 获取图片部分src
        second_result = re.findall('newkuku.*?\.jpg', img_str)[0]
        # print(second_result)
        # 拼接路径
        img_src = 'http://n2.1whour.com/' + second_result
        print(img_src)
        # 获取图片路径页面
        r = requests.get(img_src)
        # print(r.content)
        # 下载
        with open(f'{num}-{page}.jpg', 'wb') as f:
            f.write(r.content)
        time.sleep(1)
    num += 1
