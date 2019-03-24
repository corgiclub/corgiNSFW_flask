from flask import Flask, request, make_response
from httpapi.HTTPSDK import *
from pixivBot.main import main
from random import randint
import pixivpy3 as p
import random as r

# 配置路由，在插件提交返回中配置地址（如本例 http://127.0.0.1:5000）
# Create your views here.

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    req = request.get_data()
    sdk = HTTPSDK.httpGet(req)
    msg = sdk.getMsg()
    QMsg = msg.Msg
    if QMsg == "来道题":
        with open("leetcode.txt", "r", encoding="utf8") as f:
            questions = f.read().split("\n------\n")
            question = questions[randint(0, len(questions))]
            sdk.sendGroupMsg(msg.Group, question)

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
        uuid_name = uuid.uuid4().hex
        api.download(illust.image_urls[list(illust.image_urls)[-1]], path='img/', name=uuid_name + '.jpg')
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
    app.run()
