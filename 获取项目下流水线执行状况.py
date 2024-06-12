import requests
from apig_sdk import signer
from datetime import datetime
from collections import Counter
import json
import time
def sign_request(http_method, url, headers=None, body=None):
    sig = signer.Signer()
    sig.Key = "EUWCTMRJSEMOPXMQBYCQ"
    sig.Secret = "3gPhrII9WTDX1utNevxkNgbzj09SypiI7MEkS9re"
    req = signer.HttpRequest(http_method, url)
    req.headers = headers or {}
    req.body = json.dumps(body) if body else ""
    req.url = url
    sig.Sign(req)
    return req


def get_pipelines_running_status():
    url = "https://cloudpipeline-ext.cn-east-3.myhuaweicloud.com/v5/8672d4f0470f4eaf8bd75e2589934d21/api/pipelines/list"
    while True:
        body = {
            "offset": 0,
            "limit": 20
        }
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        # 使用 sign_request 函数签名请求
        req = sign_request("POST", url, headers, body)
        # 发送请求
        try:
            resp = requests.post(req.url, headers=req.headers, data=req.body)
            resp.raise_for_status()  # 确保请求成功
            # 解析并打印响应数据
            data = resp.json()
            list = []
            for i in data['pipelines']:
                # print(i['latest_run']["status"])
                list.append(i['latest_run']["status"])
            print(list)
            counter = Counter(list)
            # print(counter["RUNNING"])
            if counter["RUNNING"] == 0:
                print("前面没有运行的流水线了")
                break
        except requests.RequestException as e:
            print(f"请求发生错误: {e}")
        # 等待10秒后再次检查
        time.sleep(10)

if __name__ == '__main__':
    get_pipelines_running_status()
