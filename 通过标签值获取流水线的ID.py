# coding=utf-8
import json
import requests
from apig_sdk import signer
import configparser
import re

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

# 通过标签值获取流水线的ID
def  get_pipeline_id():
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
    try:
        resp = requests.post(req.url, headers=req.headers, data=req.body)
        resp.raise_for_status()  # 如果响应状态码不是 200，则抛出 HTTPError
        data = resp.json()
        pattern_general = 'yf'
        matched_pipelines = []
        for pipeline in data.get('pipelines', []):
            matches = re.findall(pattern_general, pipeline.get('name', ''))
            if matches:  # 如果找到匹配项
                x = "%s:%s" % (pipeline.get("name"),pipeline.get("pipeline_id"))
                matched_pipelines.append(x)
        # print(matched_pipelines)
        if len(matched_pipelines)>=2:
            for item in matched_pipelines:
                if '自动化测试' in item:  # 直接使用 in 操作符检查 'pay' 是否在字符串中
                    pipeline_id = item.split(":")[-1]
                    return pipeline_id
        elif len(matched_pipelines)==1:
            pipeline_id=matched_pipelines[0].split(":")[-1]
            print(pipeline_id)
            return pipeline_id
        else:
            print("没有找到相关的流水线")
    except requests.RequestException as e:
        print(f"Error fetching pipeline ID: {e}")
        return None
if __name__ == '__main__':
    x=get_pipeline_id()
    print(x)