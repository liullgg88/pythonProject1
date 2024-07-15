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


def run_pipeline(pipeline_id, project_id, choose_jobs, choose_stages):  # 运行流水线
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


def get_pipeline_status(project_id, pipeline_id, pipeline_run_id): # 获取某一个流水线状态
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


def get_pipeline_running_lists(project_id):  # 获取前20是个流水线运行情况
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

def get_choose_jobs_and_stages_lists(project_id, pipeline_id):
    url = f"https://cloudpipeline-ext.cn-east-3.myhuaweicloud.com/v5/{project_id}/api/pipelines/{pipeline_id}"
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
                    # 遍历作业
                    for job in stage['jobs']:
                        # 收集作业标识符
                        if "identifier" in job:
                            choose_jobs_list.append(job['identifier'])

            choose_jobs_and_stages_dict["choose_jobs"]=choose_jobs_list
            choose_jobs_and_stages_dict["choose_stages"] = choose_stages_list
            # 打印结果
            return choose_jobs_and_stages_dict
        else:
            print("响应 JSON 中缺少 'definition' 键")
    except requests.RequestException as e:
        print(f"请求错误: {e}")
    except json.JSONDecodeError as e:
        print(f"响应不是有效的 JSON: {e}")
    except KeyError as e:
        print(f"响应 JSON 中缺少键: {e}")


def  get_pipeline_id(project_id, dict_key_string):
    url = f"https://cloudpipeline-ext.cn-east-3.myhuaweicloud.com/v5/{project_id}/api/pipelines/list"
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
                if item['name'] == dict_key_string:
                    print(i['pipeline_id'])
                    return i['pipeline_id']

def create_dingtalk_message(title,pipeline_name, start_time, end_time, pipeline_run_status, server_name_string, pipeline_url): # 钉钉消息模板定义
    status_color = {
        "COMPLETED": "#32CD32",
        "FAILED": "#FF0000",
        "OTHER": "#FFA500",
        "RUNNING": "#32CD32"
    }
    color = status_color.get(pipeline_run_status, "#FFA500")
    if title=="结束":
        text = f"### CodeArts Pipeline执行{title}\n\n" \
               f"> **流水线名称:** {pipeline_name}\n\n" \
               f"> **开始时间:** {start_time}\n\n" \
               f"> **结束时间:** {end_time}\n\n" \
               f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
               f"> **链接:** [**查看详情**]({pipeline_url})\n\n" \
               f"> **此流水线由{server_name_string}等触发**\n\n" \
               f"> **自动化测试** "
    else:
        text = f"### CodeArts Pipeline执行{title}\n\n" \
               f"> **工作流名称:** {pipeline_name}\n\n" \
               f"> **开始时间:** {start_time}\n\n" \
               f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
               f"> **工作流链接:** [**查看详情**]({task_url})\n\n" \
               f"> **此流水线由{server_name_string}等触发**\n\n" \
               f"> **自动化测试** "
    return {
        "msgtype": "markdown",
        "markdown": {
            "title": "Spark Monitor",
            "text": text
        }
    }


def send_dingtalk_message(webhook_url, message):  # 发送钉钉消息
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(webhook_url, data=json.dumps(message), headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error sending DingTalk message:", e)
        sys.exit(1)

def check_process_exists(pid):  # 检查之前是否有本脚本运行的进程，如果有则等待
    """Check if a process with the given PID exists."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def wait_or_execute(pid): # 等待是否执行
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
def get_string(x):  # 字符串处理
    components = x.split(',')
    list = []
    for component in components:
        list.append(component.split("/")[1])
    # 使用切片获取前面三个值
    first_three_list = list[:3]
    # 使用join()方法将列表中的元素连接成一个字符串，元素之间用逗号加空格分隔
    server_name_string = ', '.join(first_three_list)
    return server_name_string

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='zadig调用codearts流水线信息的脚本')
    # 添加参数
    parser.add_argument('--u', '--u', type=str, required=True, help='商户名称')
    parser.add_argument('--p', '--p', type=int, required=True, help='前面运行的本脚本PID进程')
    parser.add_argument('--s', '--s', type=str, required=True, help='服务名称')

    # 解析命令行参数
    args = parser.parse_args()

    # 提取并使用参数
    dict_key_string = args.u  # 也可以使用 args.u，但建议使用更具描述性的名称
    pid = args.p
    servre_name = args.s
    if pid != 2:
        wait_or_execute(pid)
    else:
        pass
    # 从JSON文件中读取数据，获取pipeline_id
    with open('data_file.json', 'r', encoding='utf-8') as file:
        loaded_data = json.load(file)

    # 访问特定键的数据并解析其JSON字符串值
    # print(loaded_data)
    data = loaded_data[dict_key_string]
    print(data)
    project_id = "8672d4f0470f4eaf8bd75e2589934d21"
    # pipeline_id = get_pipeline_id(project_id, dict_key_string) #通过标签获取pipeline_id，目前正在测试中。。。。
    pipeline_id = data
    choose_dict = get_choose_jobs_and_stages_lists(project_id, pipeline_id)
    choose_jobs = choose_dict['choose_jobs']
    choose_stages = choose_dict['choose_stages']


    # webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token=d1b408bc9c147c819da6915baac84ac677c2f3cfbb8d2a8f7530b84e4e4974a8'
    webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token=425ff9a2f17b8143c46a951ad3eba20ff69e9b615fcb7d4b8b5bdf383dd56568'
    server_name_string = get_string(servre_name)
    get_pipeline_running_lists(project_id)
    pipeline_run_id = run_pipeline(pipeline_id, project_id, choose_jobs, choose_stages)
    if pipeline_run_id:
        title = "开始"
        task_url="https://devops.nhsoft.cn/v1/projects/detail/earth-ama/pipelines/custom/ceshihuanjing-bushu/1564?display_name=%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83-%E9%83%A8%E7%BD%B2"
        # 原始时间戳字符串，以毫秒为单位
        start_time_str = '1718939276'
        # 将字符串转换为整数，并除以1000以获得秒级的时间戳
        start_time_int = int(start_time_str)
        # 使用fromtimestamp方法将时间戳转换为datetime对象
        start_time = datetime.fromtimestamp(start_time_int)
        pipeline_name="正式环境-更新"
        pipeline_status="RUNNING"
        end_time=""
        message = create_dingtalk_message(title,
                                          pipeline_name,
                                          start_time,
                                          end_time,
                                          pipeline_status,
                                          server_name_string,
                                          task_url)
        response_text = send_dingtalk_message(webhook_url, message)
        pipeline_status = get_pipeline_status(project_id, pipeline_id, pipeline_run_id)
        if pipeline_status:
            title="结束"
            message = create_dingtalk_message(title,
                                              pipeline_status['pipeline_name'],
                                              pipeline_status['start_time'],
                                              pipeline_status['end_time'],
                                              pipeline_status['pipeline_run_status'],
                                              server_name_string,
                                              pipeline_url=f"https://devcloud.cn-east-3.huaweicloud.com/cicd/project/{project_id}/pipeline/detail/{pipeline_id}/{pipeline_run_id}?v=1")
            response_text = send_dingtalk_message(webhook_url, message)
            if pipeline_status['pipeline_run_status'] != "COMPLETED":
                print("Pipeline run did not complete successfully. Exiting.")
                sys.exit(1)
