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


def get_choose_jobs_and_stages_lists():
    url = "https://cloudpipeline-ext.cn-east-3.myhuaweicloud.com/v5/8672d4f0470f4eaf8bd75e2589934d21/api/pipelines/63755d9493c14f069e9950a2a1086ed5"
    payload = ""
    headers = {"content-type": "application/json"}

    try:
        # 假设sign_request已经正确实现并返回了请求所需的所有信息
        req = sign_request("GET", url, headers=headers, body=payload)
        resp = requests.get(req.url, headers=req.headers)
        resp.raise_for_status()  # 如果响应状态码不是 200，则抛出 HTTPError
        data = resp.json()
        choose_jobs_and_stages_dict={}
        if "definition" in data:
            # 解析definition字段中的JSON字符串
            pipeline_def = json.loads(data["definition"])

            # 初始化列表
            choose_jobs_list = []
            choose_stages_list = []

            # 遍历阶段
            for stage in pipeline_def["stages"]:
                # 收集阶段标识符
                if "identifier" in stage:
                    choose_stages_list.append(stage["identifier"])

                    # 检查是否有作业
                if "jobs" in stage:
                    for job in stage['jobs']:
                        if "identifier" in job:
                            choose_jobs_list.append(job['identifier'])

            choose_jobs_and_stages_dict["choose_jobs"]=choose_jobs_list
            choose_jobs_and_stages_dict["choose_stages"] = choose_stages_list

            return choose_jobs_and_stages_dict
        else:
            print("响应 JSON 中缺少 'definition' 键")
    except requests.RequestException as e:
        print(f"请求错误: {e}")
    except json.JSONDecodeError as e:
        print(f"响应不是有效的 JSON: {e}")
    except KeyError as e:
        print(f"响应 JSON 中缺少键: {e}")



if __name__ == '__main__':
    x=get_choose_jobs_and_stages_lists()
    print(x)