import requests
from apig_sdk import signer
from datetime import datetime
from collections import Counter
import json
import time
def sign_request(http_method, url, headers=None, body=None):
    sig = signer.Signer()
    sig.Key = "xxx"
    sig.Secret = "xxxx"
    req = signer.HttpRequest(http_method, url)
    req.headers = headers or {}
    req.body = json.dumps(body) if body else ""
    req.url = url
    sig.Sign(req)
    return req


def get_pipeline_running_lists(): #ListPipelineRuns
    url = "https://cloudpipeline-ext.cn-east-3.myhuaweicloud.com/v5/8672d4f0470f4eaf8bd75e2589934d21/api/pipelines/6310d4b5beef475eb75ba3cf40e8f729/pipeline-runs/list"

    found_not_running = False  # 用来跟踪是否找到了非RUNNING状态的流水线
    while True:
        body = {
            "offset": 0,
            "limit": 10
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
            # print(data['pipeline_runs'])
            list=[]
            for i in data['pipeline_runs']:
                list.append(i['status'])
            # 使用Counter计算每个元素的出现次数
            print(list)
            counter = Counter(list)
            # print(counter["RUNNING"])
            if counter["RUNNING"] == 0:
                print("前面没有运行的流水线了")
                break
        except requests.RequestException as e:
            print(f"请求发生错误: {e}")
        #     # 等待10秒后再次检查
        time.sleep(10)
if __name__ == '__main__':
    get_pipeline_running_lists()
