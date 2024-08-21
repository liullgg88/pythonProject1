import requests
from apig_sdk import signer
from datetime import datetime
from collections import Counter
import json
import time
import configparser
def sign_request(http_method, url, headers=None, body=None):
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


def get_pipeline_step_run_ids(project_id, pipeline_id): #获取流水线详细信息
    url = f"https://cloudpipeline-ext.cn-east-3.myhuaweicloud.com/v5/{project_id}/api/pipelines/{pipeline_id}/pipeline-runs/detail"

    payload = ""
    headers = {
        'Content-Type': 'application/json;charset=UTF-8'
    }

    # response = requests.request("GET", url, headers=headers, data=payload)
    req = sign_request("GET", url, headers=headers, body=payload)
    resp = requests.get(req.url, headers=req.headers)
    resp.raise_for_status()  # 如果响应状态码不是 200，则抛出 HTTPError
    data = resp.json()
    # 假设data中有一个名为'stages'的列表，每个阶段有一个'status'和可能的'post'列表
    for stage in data.get("stages", []):
        if stage.get("status") == "FAILED" and stage.get("post"):
            # 返回第一个失败阶段的第一个后处理的ID
            return stage["post"][0].get("id")

    # 如果没有找到失败的阶段，则返回None
    return None

def ShowStepOutputs(project_id, pipeline_id, pipeline_run_id, step_run_ids): # 获取流水线步骤执行输出
    url = f"https://cloudpipeline-ext.cn-east-3.myhuaweicloud.com/v5/{project_id}/api/pipelines/{pipeline_id}/pipeline-runs/{pipeline_run_id}/steps/outputs?step_run_ids={step_run_ids}"
    payload = ""
    headers = {
        'Content-Type': 'application/json;charset=UTF-8'
    }
    req = sign_request("GET", url, headers=headers, body=payload)
    try:
        resp = requests.get(req.url, headers=req.headers)
        resp.raise_for_status()  # 抛出异常如果HTTP请求返回了错误状态码
        data = resp.json()
        # 检查data中是否包含'step_outputs'键
        if 'step_outputs' in data:
            for step_output in data['step_outputs']:
                if 'output_result' in step_output and step_output['output_result']:
                    for result in step_output['output_result'][-1]['value']:
                        if 'ruleResults' in result:
                            for rule in result['ruleResults']:
                                if rule['status'] == "FAILED":
                                    rule_name = rule['ruleName'].split("/")[0]
                                    # step_run_id = rule["stepRunId"]
                                    # 假设fact是metricExecutionResults列表中最后一个元素的fact
                                    if 'ruleContents' in rule and rule['ruleContents']:
                                        metric_results = rule['ruleContents'][0].get('metricExecutionResults', [])
                                        if metric_results:
                                            fact = metric_results[-1].get('fact', '未知')
                                            return "%s/%s" % (rule_name,fact)

    except requests.RequestException as e:
        print(f"请求错误：{e}")
    except Exception as e:
        print(f"处理错误：{e}")
if __name__ == '__main__':
    project_id="8672d4f0470f4eaf8bd75e2589934d21"
    pipeline_id="ec563af03b884026864ce4ad5bb8253f"
    pipeline_run_id="f2bcb7891b3c45b1a5d3c429f6bd1e0b"
    step_run_ids=get_pipeline_step_run_ids(project_id, pipeline_id)
    x=ShowStepOutputs(project_id, pipeline_id, pipeline_run_id, step_run_ids)
    print(x)
