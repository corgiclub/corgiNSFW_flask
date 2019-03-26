import pixivpy3 as p
import os
import re
import random as r
import time
import threading
import json
import sys
from random import randint
from uuid import uuid4


# 热门榜
def rank_by_time(api, mode='day_male', num=1):    # (mode, date = None, offset = None) 作品排行
    json_result = api.illust_ranking(mode=mode)
    # print(json_result)
    img_list_out = []
    text = ''
    try:
        for i in range(num):
            try:
                ri = r.randint(0, len(json_result.illusts) - 1)
                illust = json_result.illusts[ri]

                # api.download(illust.image_urls['large'], path='img/', name='popular_' + str(i) + '.jpg')
                # address = os.getcwd() + '\\img\\popular_' + str(i) + '.jpg'
                uuid_name = uuid4().hex
                api.download(illust.image_urls['large'], path='img/', name=uuid_name + '.jpg')
                address = os.getcwd() + '/img/' + uuid_name + '.jpg'
                img_list_out.append(address)
                # print(illust['total_bookmarks'])
                # text = '已经收集了' + str(i+1) + '张图！'
            except IndexError:
                text = '目前只有' + str(i) + '张图QAQ'
                break
    except KeyError:
        text = '什么也没找到！你是不是输错了什么呢'
    return img_list_out, text


# 按tag搜索最热作品（按时间排序） 非会员使用
def search_by_tag_ranked(word, api, search_target='partial_match_for_tags', sort='date_desc', duration=None, p_num=15):
    img_list = []
    booked_list = []
    for pi in range(p_num):
        json_result = api.search_illust(word, search_target=search_target, sort=sort, duration=duration, p=pi + 1)
        img_list.extend(json_result.illusts)
        print('搜寻完成第' + str(pi + 1) + '面！等待5秒……')
        time.sleep(3)
    for img in img_list:
        booked_list.append(img['total_bookmarks'])
    try:
        booked_max_index = booked_list.index(max(booked_list))
        print(max(booked_list), img_list[booked_max_index])
        illust = img_list[booked_max_index]
        word = word.replace(" ", "_")
        api.download(illust.image_urls['large'], path='img/', name=word + '.jpg')
        return ['img/' + word + '.jpg'], '看最热色图！'
    except ValueError:
        return [], '没有这个tag相关的图片！'


# tag热图搜索 会员限定
def search_by_tag_popular(word, api, duration=None, num=1, p_num=2):
    img_list = []
    img_list_out = []
    for pi in range(p_num):
        json_result = api.search_illust(word, duration=duration, sort='popular_desc', p=pi)
        img_list.extend(json_result.illusts)
    try:
        for n in range(num):
            i = r.randint(0, len(img_list) - 1)
            illust = img_list[i]
            word = word.replace(" ", "_")
            uuid_name = uuid4().hex
            api.download(illust.image_urls['large'], path='img/', name=word + '_' + uuid_name + '.jpg')
            img_list_out.append(os.getcwd() + '/img/' + word + '_' + uuid_name + '.jpg')
        return img_list_out, ''
    except ValueError:
        return [], '没有这个tag相关的图片！'


# 获取tag列表
def get_tags(api):
    tags = api.trending_tags_illust()
    i = 0
    tags_list = []
    while True:
        try:
            tags_list.append(tags['trend_tags'][i]['tag'])
            i += 1
        except IndexError:
            break
    # print(tags_list)
    return tags_list


# 超时 暂时无效
def time_limit(interval):
    def wraps(func):
        def time_out():
            raise RuntimeError()

        def deco(*args, **kwargs):
            timer = threading.Timer(interval, time_out)  # interval是时限，time_out是达到实现后触发的动作
            timer.start()
            res = func(*args, **kwargs)
            timer.cancel()
            return res
        return deco
    return wraps


def main(text):
    _USERNAME = "corgiclub@yeah.net"
    _PASSWORD = "corgiclubADMIN"

    # 登录api
    api = p.AppPixivAPI()
    api.login(_USERNAME, _PASSWORD)

    # 获得输入 可接受输入：来份色图/来n份色图/来份图/来n份图/tag... 其他输入会输出'你在做什么我不太懂呀~'
    # with open("pixivBot/out.txt", "r", encoding="UTF-8") as f:
    #     text = f.read()
    # text = input()
    # text = input()
    # text = ' '.join(sys.argv[1:])
    # print(text)

    # 初始化输出
    tags_file = open('pixivBot/tags_list.json', 'r', encoding="utf8")
    tags_list = json.load(tags_file)
    output = {
        'text': '',         # 回复的消息内容
        # 'qq': 'null',         # @某qq回复
        'img_list': [],     # 要发送的图片列表
    }
    try:
        # time_limit(1)

        # 寻找当天r18色图
        donot_rush = ["别冲了", "营养跟得上吗?", "你撸多了", "别撸了,伤身体", "再冲会暴毙信不", "求求你别冲了", "冲这么多你营养跟得上?", "求求你别冲了", "冲这么多你今晚biss", "天天看色图不去读书?", "再冲jb都给你剁了", "朋友少撸管多学习"]
        img_lst = []
        if text.startswith('来') and text.endswith('色图'):
            if text.endswith('三次元色图'):
                url = 'G:/yasuo'

                if re.search('\d+', text) is None:
                    num = '1'
                else:
                    num = re.search('\d+', text).group()

                if int(num) >= 10:
                    output['text'] = donot_rush[randint(0, len(donot_rush) - 1)]
                else:
                    for i in range(int(num)):
                        for root, dirs, files in os.walk(url):
                            img_url = "G:/yasuo/" + files[randint(0, files.__len__() - 1)]
                            img_lst.append(img_url)
                    output['img_list'] = img_lst

            elif text == '来份色图':
                output['img_list'], output['text'] = rank_by_time(api, mode="day_r18")
            else:
                num = re.search('\d+', text).group()
                if int(num) >= 10:
                    output["text"] = donot_rush[randint(0, len(donot_rush) - 1)]
                else:
                    if num:
                        output['img_list'], output['text'] = rank_by_time(api, mode="day_r18", num=int(num))
                    else:
                        output['text'] = '输入有误！'

        # 当天热门榜随机
        elif text.startswith('来') and text.endswith('份图'):
            if text == '来份图':
                output['img_list'], output['text'] = rank_by_time(api, mode='day_male')
            else:
                num = re.search('\d+', text).group()
                if int(num) >= 10:
                    output["text"] = "图太多遭不住啊老哥"
                else:
                    if num:
                        output['img_list'], output['text'] = rank_by_time(api, mode='day_male', num=int(num))
                    else:
                        output['text'] = '输入有误！'
        elif text.endswith("kkp") or text.endswith("看看批"):
            url = "G:/kkp"
            n = randint(0, 10)
            if n < 8:
                output['text'] = "看你妈看"
            else:
                for root, dirs, files in os.walk(url):
                    img_url = "G:/kkp/" + files[randint(0, files.__len__() - 1)]
                    img_lst.append(img_url)
                output['img_list'] = img_lst
        # 按tag搜寻:
        elif text.startswith('tag'):
            # tag搜寻帮助
            if text == 'tag' or text.startswith('tag帮助'):
                output['text'] += '用法：\n1 “tag 标签1 标签2 ……”\n2 tag查询后按序号检索\n3 tag? 代表随机一个tag'
            # 列出推荐tag列表
            elif text == 'tag查询':
                tags_list = get_tags(api)
                for i in range(len(tags_list)):
                    output['text'] += str(i + 1) + ' ' + tags_list[i] + '\n'

            elif text == 'tag?' or text == 'tag？':
                output['img_list'], output['text'] = search_by_tag_popular(api=api, word=tags_list[randint(0, 39)])
            # 直接搜寻tag
            elif text.startswith('tag '):
                word = text[4:]
                output['img_list'], output['text'] = search_by_tag_popular(api=api, word=word)
        # 按tag列表索引
            else:
                if not tags_list:
                    output['text'] = '你还没查询过tag，不能使用tag索引！使用"tag查询"来获取tag'
                else:
                    # print(int(text[3:]) - 1)
                    output['img_list'], output['text'] = search_by_tag_popular(api=api, word=tags_list[int(text[3:]) - 1])

        elif text == '帮助':
            output['text'] = '可接受指令：\n来(n)份色图\n来(n)份图\n来(n)份三次元色图\ntag'
        # 未知输入
        else:
            output['text'] = ''

    # 报错
    # except RuntimeError():
    #     output['text'] = '超时了，网络似乎不好呢'
    except Exception as e:
        output['text'] = '又你妈宕机了'
        raise e

    # tag输出为json文件
    with open('pixivBot/tags_list.json', 'w', encoding="utf8") as fi:
        json.dump(tags_list, fi, ensure_ascii=False, indent=4)

    # 打印json
    print(json.dumps(output, ensure_ascii=False))
    with open('pixivBot/output.json', 'w', encoding="utf8") as f:
        json.dump(output, f, ensure_ascii=False)
    return output

# 全局变量
# _tags_list = []                         # tag列表
# 账号密码


# main()
