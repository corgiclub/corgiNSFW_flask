from flask import Flask, request, make_response
from httpapi.HTTPSDK import *
from pixivBot.main import main
from random import randint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4
import os
import pixivpy3 as p
import random as r
import re
import requests

# 配置路由，在插件提交返回中配置地址（如本例 http://127.0.0.1:5000）
# Create your views here.

app = Flask(__name__)
app.config.from_pyfile('settings.py')

db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    text = db.Column(db.Text)
    path = db.Column(db.String(100))
    qq = db.Column(db.String(15))
    group = db.Column(db.String(15))
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    req = request.get_data()
    sdk = HTTPSDK.httpGet(req)
    msg = sdk.getMsg()
    QMsg = msg.Msg
    print(msg)

    text = QMsg
    qq = msg.QQ
    group = msg.Group
    timestamp = datetime.now()
    if "pic" in text:
        type = 'img'
        urls = re.findall('\[IR:pic=(.+?)\]', text)
        path = ''
        if urls is not []:
            for u in urls:
                try:
                    req = requests.get(u).content
                    img_path = './dog_img/{QQ}_{uuid}.jpg'.format(QQ=qq, uuid=str(uuid4())[:8])
                    path += img_path + '\n'
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

    if QMsg == "来道题":
        pass
        # with open("leetcode.txt", "r", encoding="utf8") as f:
        #     questions = f.read().split("\n------\n")
        #     question = questions[randint(0, len(questions))]
        #     sdk.sendGroupMsg(msg.Group, question)

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
        # api.download(illust.image_urls[list(illust.image_urls)[-1]], path='img/', name=uuid_name + '.jpg')
        api.download(illust.image_urls['large'], path='img/', name=uuid_name + '.jpg')
        address = os.getcwd() + '\\img\\' + uuid_name + '.jpg'
        print(address)
        sdk.sendGroupMsg(msg.Group, "[ksust,image:pic={}]".format(address))
        sdk.sendGroupMsg(msg.Group, "https://www.pixiv.net/member_illust.php?mode=medium&illust_id={}   "
                                    "title : {}".format(id, title))

    elif (QMsg.startswith("来") and QMsg.endswith("图")) or QMsg.startswith("tag") or QMsg == "帮助" or \
            QMsg.endswith("kkp") or QMsg.endswith("看看批"):

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

    return make_response(sdk.toJsonString())


if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    app.run()
