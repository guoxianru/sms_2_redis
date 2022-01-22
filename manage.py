# -*- coding: utf-8 -*-
# @Author: GXR
# @CreateTime: 2022-01-20
# @UpdateTime: 2022-01-20

import json
import logging
import time
import traceback

import redis
from flask import Flask
from flask import request
from flask_script import Manager, Server

app = Flask(__name__)
app.debug = False
app.logger.setLevel(logging.INFO)

red = redis.Redis(
    host="127.0.0.1", port=6379, password="123456", db=0, decode_responses=True
)
redis_key = "sms_2_redis"


# 功能列表
@app.route("/", methods=["GET"], strict_slashes=False)
def index():
    try:
        return {
            "/sms_add": "添加一条短信",
            "/sms_all": "获取所有短信",
        }
    except:
        app.logger.error(traceback.format_exc())
        return {"respCode": 0, "respMsg": "服务异常", "result": {}}


# 添加一条短信
@app.route("/sms_add", methods=["POST"], strict_slashes=False)
def sms_add():
    try:
        if request.data:
            sms_info = json.loads(request.data.decode("utf-8"))["sms"]
            red.sadd(
                redis_key,
                json.dumps(
                    {
                        "phone": sms_info.split("\n")[-1],
                        "time": time.strftime(
                            "%Y-%m-%d %H:%M:%S", time.localtime(time.time())
                        ),
                        "sms": sms_info.split("\n")[1],
                    },
                    ensure_ascii=False,
                ),
            )
        return {"respCode": 0, "respMsg": "succ", "result": {}}
    except:
        app.logger.error(traceback.format_exc())
        return {"respCode": 1, "respMsg": "error", "result": {}}


# 获取所有短信
@app.route("/sms_all", methods=["GET"], strict_slashes=False)
def sms_all():
    try:
        sms_list = []
        sms_all = red.smembers(redis_key)
        for sms in sms_all:
            sms_list.append(sms)
        return {"respCode": 0, "respMsg": "succ", "result": sms_list}
    except:
        app.logger.error(traceback.format_exc())
        return {"respCode": 1, "respMsg": "error", "result": {}}


# 启动服务
def run_sms_code_api():
    manager = Manager(app)
    manager.add_command("runserver", Server("0.0.0.0", port=11004))
    manager.run()


if __name__ == "__main__":
    run_sms_code_api()
