from flask import Flask, request, make_response
from httpapi.HTTPSDK import *
from pixivBot.main import main
from random import randint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4
from flask_migrate import Migrate
from corpus import *
from whether import *
from application.repeat import *
from nltk.metrics import distance
import os
import pixivpy3 as p
import random as r
import re
import requests

switch = True
# 配置路由，在插件提交返回中配置地址（如本例 http://127.0.0.1:5000）
# Create your views here.

app = Flask(__name__)
app.config.from_pyfile('settings/flask_settings.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Message(db.Model):
    """model"""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    text = db.Column(db.Text)
    path = db.Column(db.String(100))
    qq = db.Column(db.String(15))
    group = db.Column(db.String(15))
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)


# class RecieveWord(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     recieve_word = db.Column(db.String(10), unique=True)
#
#
class SendWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(30), unique=True)


@app.route('/', methods=['GET', 'POST'])
def index() -> make_response:
    req = request.get_data()
    sdk = HTTPSDK.httpGet(req)
    msg = sdk.getMsg()
    QMsg = msg.Msg
    print(msg)
    print(QMsg)

    # 存数据库
    if msg.Group == "600302544":
        text = QMsg
        qq = msg.QQ
        group = msg.Group
        timestamp = datetime.now()
        if "pic" in text:
            type = 'img'
            urls = re.findall(':pic=(.+?)\]', text)
            path = ''
            if urls is not []:
                for u in urls:
                    try:
                        req = requests.get(u).content
                        img_path = './dog_img/{QQ}_{uuid}.jpg'.format(QQ=qq, uuid=str(uuid4())[:8])
                        path += img_path + '\n'
                        print(path)
                        with open(img_path, 'wb') as f:
                            f.write(req)
                    except Exception as e:
                        raise e
        else:
            type = 'text'
            path = 'null'

        message = Message(type=type, text=QMsg, path=path, qq=qq, group=group, timestamp=timestamp)
        db.session.add(message)
        db.session.commit()

    if get_in(QMsg):
        sdk.sendGroupMsg(msg.Group, QMsg)
        dic.clear()
        return make_response(sdk.toJsonString())
    print(dic)

    # 5%概率复读
    # if randint(0, 100) > 95:
    #     sdk.sendGroupMsg(msg.Group, QMsg)
    #     return make_response(sdk.toJsonString())

    QMsg = QMsg.replace("那", "")
    if QMsg == "来道题":
        pass
        # with open("leetcode.txt", "r", encoding="utf8") as f:
        #     questions = f.read().split("\n------\n")
        #     question = questions[randint(0, len(questions))]
        #     sdk.sendGroupMsg(msg.Group, question)

    elif QMsg.startswith("来首"):
        index = QMsg.find("首")
        music_name = QMsg[index + 1:]
        sdk.sendGroupMsg(msg.Group, "[ksust,music:name={}]".format(music_name))
    elif "天气" in QMsg and ("样" in QMsg or "如何" in QMsg):
        QMsg = QMsg.replace("那", "")
        index = QMsg.find("天气")
        status, send_msg = get_info(QMsg[:index])
        print(status)
        if status == "ok":
            sdk.sendGroupMsg(msg.Group, send_msg)
        else:
            sdk.sendGroupMsg(msg.Group, "暂不支持此地的查询")

    elif "我去" in QMsg:
        index = QMsg.find("去")
        verb = QMsg[index + 1]
        for i in verbs:
            if i in verb:
                sdk.sendGroupMsg(msg.Group, "你" + i + "个[emoji=F09F94A8],就你还" + i)
                return make_response(sdk.toJsonString())
        sdk.sendGroupMsg(msg.Group, "你" + verb + "个[emoji=F09F94A8],就你还" + verb)

    elif "去" in QMsg and "了" in QMsg:
        index1 = QMsg.find("去")
        index2 = QMsg.find("了")
        for i in verbs:
            if i in QMsg[index2:index1:-1]:
                sdk.sendGroupMsg(msg.Group, "你" + i + "个[emoji=F09F94A8]")
                break

    elif "让我康康" in QMsg:
        _USERNAME = "corgiclub@yeah.net"
        _PASSWORD = "corgiclubADMIN"
        api = p.AppPixivAPI()
        api.login(_USERNAME, _PASSWORD)
        json_result = api.illust_ranking(mode='week')
        ri = r.randint(0, len(json_result.illusts) - 1)
        illust = json_result.illusts[ri]
        id = illust.id
        title = illust.title
        uuid_name = uuid4().hex
        api.download(illust.image_urls['large'], path='img/', name=uuid_name + '.jpg')
        address = os.getcwd() + '\\img\\' + uuid_name + '.jpg'
        print(address)
        sdk.sendGroupMsg(msg.Group, "[ksust,image:pic={}]".format(address))
        sdk.sendGroupMsg(msg.Group, "https://www.pixiv.net/member_illust.php?mode=medium&illust_id={}   "
                                    "title : {}".format(id, title))

    elif (QMsg.startswith("来") and QMsg.endswith("图")) or QMsg.startswith("tag") or QMsg == "帮助" or \
            QMsg.endswith("kkp") or QMsg.endswith("看看批"):
        if randint(0, 100) > 80:
            sdk.sendGroupMsg(msg.Group, "来你妈来")
            if randint(0, 100) > 50:
                sdk.sendGroupMsg(msg.Group, SendWord.query.get(randint(1, SendWord.query.count())).word)
            return make_response(sdk.toJsonString())

        resp = main(QMsg)

        # ---------------PRODUCT MODE---------------------------

        if msg.Type == HTTPSDK.TYPE_GROUP:
            if resp["text"] != "":
                sdk.sendGroupMsg(msg.Group, resp["text"])
            if resp["img_list"] is not None:
                length = len(resp["img_list"])
                for i in range(length):
                    addr = resp["img_list"][i]
                    sdk.sendGroupMsg(msg.Group, "[ksust,image:pic={}]".format(addr))

        # ---------------DEBUG MODE---------------------------

        # if msg.Type == HTTPSDK.TYPE_FRIEND:
        #     if resp["text"] != "":
        #         sdk.sendPrivdteMsg(msg.QQ, resp["text"])
        #     if resp["img_list"] != None:
        #         length = len(resp["img_list"])
        #         for i in range(length):
        #             addr = resp["img_list"][i]
        #             sdk.sendPrivdteMsg(msg.QQ, "[ksust,image:pic={}]".format(addr))

        # ---------------DEBUG MODE---------------------------

    elif "at=3254622926" in QMsg or "at=1045970957" in QMsg:
        pattern = "".join(re.findall(r"\[(?:QQ)?(?:IR)?:at=(?:3254622926)?(?:1045970957)?\] ", QMsg))
        if pattern == QMsg:
            sdk.sendGroupMsg(msg.Group, "@我干啥")
            return make_response(sdk.toJsonString())
        for record in SendWord.query.all():
            if record.word in QMsg:
                sdk.sendGroupMsg(msg.Group, SendWord.query.get(randint(1, SendWord.query.count())).word)
                if randint(0, 100) > 60:
                    sdk.sendGroupMsg(msg.Group, SendWord.query.get(randint(1, SendWord.query.count())).word)
                if randint(0, 100) > 90:
                    sdk.sendGroupMsg(msg.Group, SendWord.query.get(randint(1, SendWord.query.count())).word)
                return make_response(sdk.toJsonString())
        record = QMsg.replace(pattern, "").strip()
        word = SendWord(word=record)
        db.session.add(word)
        db.session.commit()

        sdk.sendGroupMsg(msg.Group, "学到了,下次就用这话骂你")

    return make_response(sdk.toJsonString())


if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    app.run(port=9999)
