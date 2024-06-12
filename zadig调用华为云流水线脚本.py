# coding=utf-8
import json
import requests
from apig_sdk import signer
from datetime import datetime
from collections import Counter
import sys
import time
import os

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


def get_pipeline_running_lists(project_id):
    url = f"https://cloudpipeline-ext.cn-east-3.myhuaweicloud.com/v5/{project_id}/api/pipelines/list"
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
            # print(list)
            counter = Counter(list)
            # print(counter["RUNNING"])
            if counter["RUNNING"] == 0:
                print("前面没有运行的流水线了")
                break
        except requests.RequestException as e:
            print(f"请求发生错误: {e}")
        # 等待10秒后再次检查
        time.sleep(10)

def create_dingtalk_message(title,pipeline_name, start_time, end_time, pipeline_run_status, pipeline_url):
    status_color = {
        "COMPLETED": "#32CD32",
        "FAILED": "#FF0000",
        "OTHER": "#FFA500",
        "RUNNING": "#32CD32"
    }
    color = status_color.get(pipeline_run_status, "#FFA500")
    text = f"### CodeArts Pipeline执行{title}\n\n" \
           f"> **流水线名称:** {pipeline_name}\n\n" \
           f"> **开始时间:** {start_time}\n\n" \
           f"> **结束时间:** {end_time}\n\n" \
           f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
           f"> **链接:** [**查看详情**]({pipeline_url})\n\n" \
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

def check_process_exists(pid):
    """Check if a process with the given PID exists."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def wait_or_execute(pid):
    """Wait for a process with the given PID to exit, or execute a command if it doesn't exist."""
    if check_process_exists(pid):
        print(f"Process {pid} exists, waiting...")
        # 这里我们使用简单的轮询来模拟等待，但这不是最高效的方法
        # 在实际应用中，你可能需要更复杂的逻辑或第三方库来等待进程
        while check_process_exists(pid):
            time.sleep(1)  # 等待1秒然后再次检查
        print(f"Process {pid} has exited.")
    else:
        print(f"Process {pid} does not exist, executing command: ")


if __name__ == '__main__':
    dict_mapping = {
        # "retail-lll": '{"pipeline_id": "d7580ec1f3ab4f7bae2028c8bd5c66cd", "choose_jobs": ["168864794392314618d37-850e-46c8-b911-d2d644b19430"], "choose_stages": [0]}',
        "sy": '{"pipeline_id": "992cad1f95a5464596a17cf55d0794de", "choose_jobs": ["JOB_femhb", "JOB_ZyTPf", "JOB_XdteN", "JOB_cPDNy", "JOB_BefDX", "JOB_GfHZS", "JOB_CbzCy", "JOB_Ackpb", "JOB_XkZbc", "JOB_fFCQy", "JOB_mhZsG", "JOB_mrCQY", "JOB_KDAYk", "JOB_dFEMT", "JOB_mDZsf"], "choose_stages": ["17161900014471ce96304-6365-4e00-8c1e-136372246a89", "1716295607057e725c98b-11a6-4d5d-9289-62b2725e2b69", "171629560859755a6814c-eb11-4d29-8bf8-62488b59262f", "1716190061661a6292fde-0d90-46e2-a91d-afc757a3d029", "17162958907471778fcc3-0bbe-4a09-a561-313c295d2c0f"]}',
        "ybj": '{"pipeline_id": "453d29bada834d18872b8d95c715b494", "choose_jobs": ["JOB_femhb", "JOB_ZyTPf", "JOB_XdteN", "JOB_cPDNy", "JOB_BefDX", "JOB_GfHZS", "JOB_CbzCy", "JOB_Ackpb", "JOB_XkZbc", "JOB_fFCQy", "JOB_mhZsG", "JOB_mrCQY", "JOB_KDAYk", "JOB_FhiBC"], "choose_stages": ["17161900014471ce96304-6365-4e00-8c1e-136372246a89","1716295607057e725c98b-11a6-4d5d-9289-62b2725e2b69","171629560859755a6814c-eb11-4d29-8bf8-62488b59262f","1716190061661a6292fde-0d90-46e2-a91d-afc757a3d029","17162958907471778fcc3-0bbe-4a09-a561-313c295d2c0f"]}',
        "txp": '{"pipeline_id": "6310d4b5beef475eb75ba3cf40e8f729", "choose_jobs": ["JOB_femhb", "JOB_STzDY", "JOB_iCFKi", "JOB_YFDiz", "JOB_wybKt", "JOB_GSbrw", "JOB_ZyTPf", "JOB_XdteN", "JOB_cPDNy", "JOB_BefDX", "JOB_GfHZS", "JOB_fFCQy", "JOB_XkZbc", "JOB_mhZsG", "JOB_mrCQY", "JOB_KDAYk", "JOB_CbzCy", "JOB_Ackpb", "JOB_xKYKx", "JOB_BRXAc", "JOB_sxFGX", "JOB_YJFHa"], "choose_stages": ["17161900014471ce96304-6365-4e00-8c1e-136372246a89",  "171646779570881e9dc2b-9ce9-4688-9c2a-eae996ca5f89",  "1716295607057e725c98b-11a6-4d5d-9289-62b2725e2b69",  "1716190061661a6292fde-0d90-46e2-a91d-afc757a3d029",  "171629560859755a6814c-eb11-4d29-8bf8-62488b59262f",  "17168032167746c5678d4-0eed-4ef2-8fdf-8cecb8bbd878"]}',
        "lswj": '{"pipeline_id": "d68c72766c194c18b45569198cad1558", "choose_jobs": ["JOB_femhb", "JOB_STzDY", "JOB_iCFKi", "JOB_YFDiz", "JOB_wybKt", "JOB_GSbrw", "JOB_ZyTPf", "JOB_XdteN", "JOB_cPDNy", "JOB_BefDX", "JOB_GfHZS",  "JOB_fFCQy", "JOB_XkZbc", "JOB_mhZsG", "JOB_mrCQY", "JOB_KDAYk", "JOB_CbzCy", "JOB_Ackpb", "JOB_xKYKx", "JOB_BRXAc", "JOB_sxFGX", "JOB_zaxxJ", "JOB_XzEEk" ], "choose_stages": ["17161900014471ce96304-6365-4e00-8c1e-136372246a89","171646779570881e9dc2b-9ce9-4688-9c2a-eae996ca5f89","1716295607057e725c98b-11a6-4d5d-9289-62b2725e2b69","1716190061661a6292fde-0d90-46e2-a91d-afc757a3d029","171629560859755a6814c-eb11-4d29-8bf8-62488b59262f","17168032167746c5678d4-0eed-4ef2-8fdf-8cecb8bbd878"]}',
        "lrsp": '{"pipeline_id": "9a53d6dd35854d06aa67f04119c2fd22", "choose_jobs": ["JOB_femhb","JOB_STzDY","JOB_iCFKi","JOB_YFDiz","JOB_wybKt","JOB_GSbrw","JOB_ZyTPf","JOB_XdteN","JOB_cPDNy","JOB_BefDX","JOB_GfHZS","JOB_fFCQy","JOB_XkZbc","JOB_mhZsG","JOB_mrCQY","JOB_KDAYk","JOB_CbzCy","JOB_Ackpb","JOB_xKYKx","JOB_BRXAc","JOB_sxFGX","JOB_zaxxJ","JOB_Qyism"], "choose_stages": ["17161900014471ce96304-6365-4e00-8c1e-136372246a89", "171646779570881e9dc2b-9ce9-4688-9c2a-eae996ca5f89", "1716295607057e725c98b-11a6-4d5d-9289-62b2725e2b69", "1716190061661a6292fde-0d90-46e2-a91d-afc757a3d029", "171629560859755a6814c-eb11-4d29-8bf8-62488b59262f",  "17168032167746c5678d4-0eed-4ef2-8fdf-8cecb8bbd878"]}',
        "qhpz": '{"pipeline_id": "3da14ab66c85481f8938571e25d50e36", "choose_jobs": ["JOB_femhb","JOB_ZyTPf","JOB_XdteN","JOB_cPDNy","JOB_BefDX","JOB_GfHZS","JOB_CbzCy","JOB_Ackpb","JOB_XkZbc","JOB_fFCQy","JOB_mhZsG","JOB_mrCQY","JOB_KDAYk","JOB_FhiBC" ], "choose_stages": ["17161900014471ce96304-6365-4e00-8c1e-136372246a89","1716295607057e725c98b-11a6-4d5d-9289-62b2725e2b69","171629560859755a6814c-eb11-4d29-8bf8-62488b59262f","1716190061661a6292fde-0d90-46e2-a91d-afc757a3d029","17162958907471778fcc3-0bbe-4a09-a561-313c295d2c0f" ]}',
        "qhj": '{"pipeline_id": "0ed51aafb4ed4bebb2ae1ece1421a278", "choose_jobs": ["JOB_femhb", "JOB_STzDY", "JOB_iCFKi", "JOB_YFDiz","JOB_wybKt","JOB_GSbrw","JOB_ZyTPf","JOB_XdteN","JOB_cPDNy","JOB_BefDX", "JOB_GfHZS", "JOB_fFCQy", "JOB_XkZbc", "JOB_mhZsG", "JOB_mrCQY", "JOB_KDAYk", "JOB_CbzCy", "JOB_Ackpb","JOB_xKYKx","JOB_BRXAc", "JOB_sxFGX", "JOB_dFEMT"], "choose_stages": ["17161900014471ce96304-6365-4e00-8c1e-136372246a89","171646779570881e9dc2b-9ce9-4688-9c2a-eae996ca5f89","1716295607057e725c98b-11a6-4d5d-9289-62b2725e2b69", "1716190061661a6292fde-0d90-46e2-a91d-afc757a3d029", "171629560859755a6814c-eb11-4d29-8bf8-62488b59262f", "1716295891537606dcec9-799b-4463-9d14-7d263992646c"]}',
        "lshnh": '{"pipeline_id": "49ff9b938d744d299d71112c3ad776d2", "choose_jobs": ["JOB_femhb","JOB_STzDY","JOB_iCFKi","JOB_YFDiz","JOB_wybKt","JOB_GSbrw","JOB_ZyTPf","JOB_XdteN","JOB_cPDNy","JOB_BefDX","JOB_GfHZS","JOB_CbzCy","JOB_Ackpb","JOB_xKYKx","JOB_BRXAc","JOB_sxFGX","JOB_fFCQy","JOB_XkZbc","JOB_mhZsG","JOB_mrCQY","JOB_KDAYk","JOB_zaxxJ"], "choose_stages": ["17161900014471ce96304-6365-4e00-8c1e-136372246a89", "171646779570881e9dc2b-9ce9-4688-9c2a-eae996ca5f89", "1716295607057e725c98b-11a6-4d5d-9289-62b2725e2b69", "171629560859755a6814c-eb11-4d29-8bf8-62488b59262f", "1716190061661a6292fde-0d90-46e2-a91d-afc757a3d029", "17168032167746c5678d4-0eed-4ef2-8fdf-8cecb8bbd878"]}',
        "retail-nnn": '{"pipeline_id": "third_id", "choose_jobs": [], "choose_stages": []}',
        # "retail-nnn": '{"pipeline_id": "third_id", "choose_jobs": [], "choose_stages": []}',
        # 可以继续添加更多键值对...
    }
    dict_key_string = sys.argv[1]
    pid = int(sys.argv[2])
    if pid != 2:
        wait_or_execute(pid)
    else:
        pass
    data = json.loads(dict_mapping[dict_key_string])
    # print(data)
    # data = {"pipeline_id": "d7580ec1f3ab4f7bae2028c8bd5c66cd", "choose_jobs": "168864794392314618d37-850e-46c8-b911-d2d644b19430", "choose_stages": 0}
    project_id = "8672d4f0470f4eaf8bd75e2589934d21"
    pipeline_id = data['pipeline_id']
    choose_jobs = data['choose_jobs']
    choose_stages = data['choose_stages']


    # webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token=d1b408bc9c147c819da6915baac84ac677c2f3cfbb8d2a8f7530b84e4e4974a8'
    webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token=425ff9a2f17b8143c46a951ad3eba20ff69e9b615fcb7d4b8b5bdf383dd56568'
    get_pipeline_running_lists(project_id)
    pipeline_run_id = run_pipeline(pipeline_id, project_id, choose_jobs, choose_stages)
    if pipeline_run_id:
        #title = "开始"
        # message = create_dingtalk_message(title,
        #                                   pipeline_status['pipeline_name'],
        #                                   pipeline_status['start_time'],
        #                                   pipeline_status['end_time'],
        #                                   pipeline_status['pipeline_run_status'],
        #                                   pipeline_url=f"https://devcloud.cn-east-3.huaweicloud.com/cicd/project/{project_id}/pipeline/detail/{pipeline_id}/{pipeline_run_id}?v=1")
        # response_text = send_dingtalk_message(webhook_url, message)
        pipeline_status = get_pipeline_status(project_id, pipeline_id, pipeline_run_id)
        if pipeline_status:
            title="结束"
            message = create_dingtalk_message(title,
                                              pipeline_status['pipeline_name'],
                                              pipeline_status['start_time'],
                                              pipeline_status['end_time'],
                                              pipeline_status['pipeline_run_status'],
                                              pipeline_url=f"https://devcloud.cn-east-3.huaweicloud.com/cicd/project/{project_id}/pipeline/detail/{pipeline_id}/{pipeline_run_id}?v=1")
            response_text = send_dingtalk_message(webhook_url, message)
            if pipeline_status['pipeline_run_status'] != "COMPLETED":
                print("Pipeline run did not complete successfully. Exiting.")
                sys.exit(1)