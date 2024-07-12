# coding=utf-8
import json
import requests
from apig_sdk import signer
from datetime import datetime
import sys
import time


def sign_request(http_method, url, headers=None, body=None):
    sig = signer.Signer()
    sig.Key = "xxxx"
    sig.Secret = "xxxx"
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
    return data.get('pipeline_run_id')


def get_pipeline_status(project_id, pipeline_id, pipeline_run_id):
    url = f"https://cloudpipeline-ext.cn-east-3.myhuaweicloud.com/v5/{project_id}/api/pipelines/{pipeline_id}/pipeline-runs/detail?pipeline_run_id={pipeline_run_id}"
    while True:
        req = sign_request("GET", url, headers={"content-type": "application/json"})
        response = requests.get(req.url, headers=req.headers)
        data = response.json()
        pipeline_run_status = data.get('status')
        if pipeline_run_status != "RUNNING":
            pipeline_name = data.get('name')
            start_time = datetime.fromtimestamp(data.get('start_time') / 1000)
            end_time = datetime.fromtimestamp(data.get('end_time') / 1000)
            return {
                'pipeline_name': pipeline_name,
                'pipeline_run_status': pipeline_run_status,
                'start_time': start_time,
                'end_time': end_time
            }
        time.sleep(10)

def create_dingtalk_message(pipeline_name, start_time, end_time, pipeline_run_status, pipeline_url):
    status_color = {
        "COMPLETED": "#32CD32",
        "FAILED": "#FF0000",
        "OTHER": "#FFA500"
    }
    color = status_color.get(pipeline_run_status, "#FFA500")
    text = f"### {pipeline_name} 测试用例完成\n\n" \
           f"> **流水线名称:** {pipeline_name}\n\n" \
           f"> **开始时间:** {start_time}\n\n" \
           f"> **结束时间:** {end_time}\n\n" \
           f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
           f"> [**流水线地址**]({pipeline_url})\n\n" \
           f"> **自动化测试** "
    return {
        "msgtype": "markdown",
        "markdown": {
            "title": "Spark Monitor",
            "text": text
        }
    }


def send_dingtalk_message(webhook_url, message):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(webhook_url, data=json.dumps(message), headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error sending DingTalk message:", e)
        sys.exit(1)


if __name__ == '__main__':
    test_mapping = {
        "retail-lll": '{"pipeline_id": "d7580ec1f3ab4f7bae2028c8bd5c66cd", "choose_jobs": "168864794392314618d37-850e-46c8-b911-d2d644b19430", "choose_stages": 0}',
        "retail-mmm": '{"pipeline_id": "another_id", "choose_jobs": "another_job_id", "choose_stages": 1}',
        "retail-nnn": '{"pipeline_id": "third_id", "choose_jobs": "third_job_id", "choose_stages": 2}',
        # 可以继续添加更多键值对...
    }
    # json_string = sys.argv[1]
    ven_string = sys.argv[1]
    data = json.loads(test_mapping[ven_string])
    # print(data)
    # data = {"pipeline_id": "d7580ec1f3ab4f7bae2028c8bd5c66cd", "choose_jobs": "168864794392314618d37-850e-46c8-b911-d2d644b19430", "choose_stages": 0}
    project_id = "8672d4f0470f4eaf8bd75e2589934d21"
    pipeline_id = data['pipeline_id']
    choose_jobs = [data['choose_jobs']]
    choose_stages = [data['choose_stages']]
    # pipeline_id = "${PipelineID}"
    # project_id = "${ProjectID}"
    # choose_jobs = ["${choose_jobs}"]
    # choose_stages = ["${choose_stages}"]

    # webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token=c8fd136bc08598e3a9a4b9cb8b6ea7de80506f3ef5f221f586bc867ad7979227'
    webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token=425ff9a2f17b8143c46a951ad3eba20ff69e9b615fcb7d4b8b5bdf383dd56568'

    pipeline_run_id = run_pipeline(pipeline_id, project_id, choose_jobs, choose_stages)
    if pipeline_run_id:
        pipeline_status = get_pipeline_status(project_id, pipeline_id, pipeline_run_id)
        if pipeline_status:
            message = create_dingtalk_message(pipeline_status['pipeline_name'],
                                              pipeline_status['start_time'],
                                              pipeline_status['end_time'],
                                              pipeline_status['pipeline_run_status'],
                                              pipeline_url=f"https://devcloud.cn-east-3.huaweicloud.com/cicd/project/{project_id}/pipeline/detail/{pipeline_id}/{pipeline_run_id}?v=1")
            response_text = send_dingtalk_message(webhook_url, message)
            if pipeline_status['pipeline_run_status'] != "COMPLETED":
                print("Pipeline run did not complete successfully. Exiting.")
                sys.exit(1)
            print(response_text)
