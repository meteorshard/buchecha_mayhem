#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
import os
from bs4 import BeautifulSoup

proxies = {'http': 'http://127.0.0.1:1087',
           'https': 'http://127.0.0.1:1087'}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Referer": "https://www.buchechaonline.com/"
}

cookies = {'wordpress_logged_in_5acdfe3b17d89f0ca1183ac0796b75d9': 'meteorshard%7C1521526253%7C1exSEksYRyCB21AM4c0e66YKv4aafjQdxF9EAkJWb93%7Cbb3ff703fb04861c4ecd85824669f25a2d8dee45f646838da6374f0191f18b5b',
           'wp_woocommerce_session_5acdfe3b17d89f0ca1183ac0796b75d9': '796992461bf7924d6b5943e0df48eb99%7C%7C1520489446%7C%7C1520485846%7C%7C7d114a7f8383f48f2a12ac5f06b632d2'}
video_pages_global = []


'-----按照分类解析列表页面查找播放页面地址-----'
def get_video_page_url(categories):

    for each_category in categories:
        for page_number in range(1,9999):
            index_url = 'https://www.buchechaonline.com/videos_categories/{}/page/{}/'.format(each_category, page_number)
            print('解析页面: {}'.format(index_url))
            r = requests.get(url=index_url, cookies=cookies, headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')

            # Check if the page exists
            valid_check = soup.find_all(text='Error 404. We didn\'t find anything. Try searching!')
            if valid_check:
                break

            video_pages_raw = soup.find_all('div', 'entry-title')
            for each_raw in video_pages_raw:
                download_video_from(each_raw.a.get('href'))


'-----解析播放页面获得视频文件实际地址-----'
def download_video_from(url):
    # Check if the file already exists
    file_name_pattern = re.compile(r'(?<=https://www.buchechaonline.com/video/).*?(?=/)')
    file_name = './downloaded/{}.mp4'.format(file_name_pattern.findall(url)[0])

    if os.path.exists(file_name):
        print('文件"{}"已存在不需要下载'.format(file_name))
        return -1

    # Get iframe src
    s = requests.session()
    detail_page = s.get(url=url, cookies=cookies, headers=headers)
    soup = BeautifulSoup(detail_page.content, 'html.parser')

    if soup.find('iframe'):
        iframe_src = soup.find('iframe').get('src')

        print('正在从视频播放页面{}解析文件地址'.format(url))
        print('视频播放框架地址为{}'.format(iframe_src))

        # # Get the file url of the video
        video_player = s.get(iframe_src, headers=headers, cookies=cookies, proxies=proxies)

        pattern = re.compile(r'(?<="progressive":)\[.*?\]')
        result = list(pattern.findall(video_player.content))[0]

        # Seach 720p video file
        video_urls = {}
        url_pattern = re.compile(r'https://.*?"')
        for each_video in result.split('},'):
            if (each_video.find('720p')!=-1):
                video_url = re.findall(url_pattern, each_video)[0][:-1]
                video_urls['720p'] = video_url
                print('找到720p文件，地址是:\n{}\n-----'.format(video_url))
            elif (each_video.find('1080p')!=-1):
                video_url = re.findall(url_pattern, each_video)[0][:-1]
                video_urls['1080p'] = video_url
                print('找到1080p文件，地址是:\n{}\n-----'.format(video_url))
            elif (each_video.find('480p')!=-1):
                video_url = re.findall(url_pattern, each_video)[0][:-1]
                video_urls['480p'] = video_url
                print('找到480p文件，地址是:\n{}\n-----'.format(video_url))
            elif (each_video.find('360p')!=-1):
                video_url = re.findall(url_pattern, each_video)[0][:-1]
                video_urls['360p'] = video_url
                print('找到360p文件，地址是:\n{}\n-----'.format(video_url))

        if video_urls:
            priorities = ['720p','1080p','480p','360p']
            for each_priority in priorities:
                if each_priority in video_urls:
                    video_url_to_download = video_urls[each_priority]
                    print('即将下载{}文件: {}'.format(each_priority, video_url_to_download))
                    break
        else:
            print('找不到视频文件')
            return -1

        video_file = s.get(url=video_url_to_download, cookies=cookies, headers=headers)

        print('正在保存文件到{}...'.format(file_name))
        with open(file_name,'wb') as file:
            file.write(video_file.content)
        print('文件保存完成')

    else:
        print('视频链接坏球')
        return -1


if __name__ == '__main__':
    get_video_page_url(['all-videos'])
