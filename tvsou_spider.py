# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

channels_file = 'tvsou.txt'
epg_file = 'e.xml'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33"
}

def get_channels():
    channels_dict = {}
    with open(channels_file, 'r', encoding='utf-8') as r:
        for channel in r:
            channels_dict[channel.split()[0]] = channel.split()[1]
    return channels_dict

def get_urls(channel_id):
    urls = []
    start_week = datetime.today().isoweekday()
    while start_week <= 7:
        url = 'https://www.tvsou.com/epg/' + f'{channel_id}/w' + str(start_week)
        urls.append(url)
        start_week += 1
    return urls

def write_channel():
    with open(epg_file, 'w', encoding="utf8") as w:
        w.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        w.write("<tv >\n")

    channels_dict = get_channels()
    with open(epg_file, 'a', encoding="utf8") as w:
        for channel_name in channels_dict.values():
            w.write(f'	<channel id="{channel_name}">\n')
            w.write(f'		<display-name lang="zh">{channel_name}</display-name>\n')
            w.write("	</channel>\n")

def format_time(time, increase):
    date = str(datetime.today() + timedelta(increase))[0:10].replace('-', '')
    f_time = date + time.replace(':', '') + '00 +0800'
    return f_time

def write_programme(channel, start_time, stop_time, programme, increase):
    with open(epg_file, 'a', encoding="utf8") as w:
        w.write(f'	<programme channel="{channel}" start="{format_time(start_time, increase)}"'
                f' stop="{format_time(stop_time, increase)}">\n')
        w.write(f'		<title lang="zh">{programme}</title>\n')
        w.write('	</programme>\n')

def write_programme_all(channels_num):
    for channel_num, channel_name in channels_num.items():
        urls = get_urls(channel_num)
        increase = 0
        for url in urls:
            programme_list = get_programme_list(url)
            for start_time, tv_program in programme_list.items():
                i = list(programme_list.keys()).index(start_time)
                try:
                    end_time = list(programme_list.keys())[i+1]
                except IndexError:
                    end_time = '23:59'
                write_programme(channel_name, start_time, end_time, tv_program, increase)
            increase += 1

    with open(epg_file, 'a', encoding="utf8") as w:
        w.write('</tv>')

def get_programme_list(url):
    content = requests.get(url=url, headers=headers).content
    soup = BeautifulSoup(content, 'lxml')
    res = soup.find_all(name='table', attrs={'class': 'layui-table c_table'})
    res_tv_program = res[0].find_all(name='td')
    res_tv_program_list = [res_tv_program[i].text for i in range(0, len(res_tv_program))]

    # 去除空方法一
    # res_tv_program_list_filter = [i for i in res_tv_program_list if i != '']
    # 去除空方法二，得到filter类，用list()函数转换为列表
    # res_tv_program_list_filter = list(filter(None, res_tv_program_list))

    #利用切片提取时间和节目，时间从0开始，每3个截取一个，节目从1开始，每3个截取一个
    tv_time = res_tv_program_list[::3]
    tv_program = res_tv_program_list[1::3]

    # 利用zip函数把时间和节目转换成字典
    programme_list = dict(zip(tv_time, tv_program))
    return programme_list


if __name__ == '__main__':
    write_channel()
    channels_id = get_channels()
    write_programme_all(channels_id)
