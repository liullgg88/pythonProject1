# coding=utf-8
import json
import requests
from apig_sdk import signer
from datetime import datetime
from collections import Counter
import sys
import time
import os
import argparse
import configparser


def sign_request(http_method, url, headers=None, body=None): # 获取登录认证密钥
    sig = signer.Signer()
    config = configparser.ConfigParser()
    config.read('secretkey.ini')
    sig.Key = config['Sig']['Key']
    sig.Secret = config['Sig']['Secret']
    req = signer.HttpRequest(http_method, url)
    req.headers = headers or {}
    req.body = json.dumps(body) if body else ""
    req.url = url
    sig.Sign(req)
    return req

def  get_pipelines_id():
    url = "https://cloudpipeline-ext.cn-east-3.myhuaweicloud.com/v5/8672d4f0470f4eaf8bd75e2589934d21/api/pipelines/list"
    payload  = {
        "offset": 0,
        "limit": 200
    }
    headers = {
        'Content-Type': 'application/json;charset=UTF-8'
    }
    # 使用 sign_request 函数签名请求
    req = sign_request("POST", url, headers=headers, body=payload)
    resp = requests.post(req.url, headers=req.headers, data=req.body)
    resp.raise_for_status()  # 如果响应状态码不是 200，则抛出 HTTPError
    data = resp.json()
    for i in data['pipelines']:
        if i['tag_list']:
            for item in i['tag_list']:
                # 标签值为als
                if item['name'] == "als":
                    # print(i['pipeline_id'])
                    return i['pipeline_id']
if __name__ == '__main__':
    get_pipelines_id()