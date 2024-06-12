# coding=utf-8
import json
import requests
from apig_sdk import signer
from datetime import datetime
from collections import Counter
import sys
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

def run_pipeline(pipeline_id, project_id, choose_jobs, choose_stages):
    url = f"https://cloudpipeline-ext.cn-east-3.myhuaweicloud.com/v5/{project_id}/api/pipelines/{pipeline_id}/run"
    headers = {"content-type": "application/json"}
    body = {
        "sources": [],
        "description": "",
        "variables": [],
        "choose_jobs": choose_jobs,
        "choose_stages": choose_stages
    }
    req = sign_request("POST", url, headers=headers, body=body)
    resp = requests.post(req.url, headers=req.headers, data=req.body)
    data = resp.json()
    print(data)
    # return data.get('pipeline_run_id')


if __name__ == '__main__':
    dict_mapping = {
        "retail-lll": '{"pipeline_id": "d7580ec1f3ab4f7bae2028c8bd5c66cd", "choose_jobs": ["168864794392314618d37-850e-46c8-b911-d2d644b19430"], "choose_stages": [0]}',
        # "retail-nnn": '{"pipeline_id": "third_id", "choose_jobs": [], "choose_stages": []}',
        # 可以继续添加更多键值对...
    }
    # json_string = sys.argv[1]
    dict_key_string = "retail-lll"
    data = json.loads(dict_mapping[dict_key_string])
    # print(data)
    # data = {"pipeline_id": "d7580ec1f3ab4f7bae2028c8bd5c66cd", "choose_jobs": "168864794392314618d37-850e-46c8-b911-d2d644b19430", "choose_stages": 0}
    project_id = "8672d4f0470f4eaf8bd75e2589934d21"
    pipeline_id = data['pipeline_id']
    choose_jobs = data['choose_jobs']
    choose_stages = data['choose_stages']
    run_pipeline(pipeline_id, project_id, choose_jobs, choose_stages)