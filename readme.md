# 机器人的flask重构版本  
>示例代码      

    from flask import Flask, request, make_response
    from httpapi.HTTPSDK import *
    
    # 配置路由，在插件提交返回中配置地址（如本例 http://127.0.0.1:5000）
    # Create your views here.
    
    app = Flask(__name__)
    
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        req = request.get_data()
        sdk = HTTPSDK.httpGet(req)
        print(sdk.getMsg())
    
        sdk.sendPrivdteMsg(sdk.getMsg().QQ, '你发送了这样的消息：' + sdk.getMsg().Msg)
        sdk.getLoginQQ()
    
        # 回调演示，提交返回获取群列表、登录QQ等
        if sdk.isCallback() and sdk.getMsg().Type == HTTPSDK.TYPE_GET_LOGIN_QQ:
            print('Login QQ:' + str(sdk.getLoginQQ()))
    
        return make_response(sdk.toJsonString())
    
    
    if __name__ == '__main__':
        app.run()

# 项目结构
corgiNSFW_flask/   
&ensp;&ensp;&ensp;&ensp;img/    &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;图片存储位置  
&ensp;&ensp;&ensp;&ensp;pixivBot/  &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;bot文件夹  
&ensp;&ensp;&ensp;&ensp;pixivpy3/  &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;爬p站的库  
&ensp;&ensp;&ensp;&ensp;app.py &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;主程序  


# 使用方法
装好该装的依赖   
>flask  
flask-sqlalchemy  
requests      

然后运行 app.py

# 更新中...

