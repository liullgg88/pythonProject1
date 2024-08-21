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
import re
from dingtalkchatbot.chatbot import DingtalkChatbot


webhook = 'https://oapi.dingtalk.com/robot/send?access_token=425ff9a2f17b8143c46a951ad3eba20ff69e9b615fcb7d4b8b5bdf383dd56568'
ding_talk = DingtalkChatbot(webhook)

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
    try:
        resp = requests.post(req.url, headers=req.headers, data=req.body)
        resp.raise_for_status()  # 如果响应状态码不是 200，则抛出 HTTPError
        data = resp.json()
        pattern_general = dict_key_string
        matched_pipelines = []
        for pipeline in data.get('pipelines', []):
            matches = re.findall(pattern_general, pipeline.get('name', ''))
            if matches:  # 如果找到匹配项
                x = "%s:%s" % (pipeline.get("name"), pipeline.get("pipeline_id"))
                matched_pipelines.append(x)
        # print(matched_pipelines)
        if len(matched_pipelines) >= 2:
            for item in matched_pipelines:
                if '自动化测试' in item:  # 直接使用 in 操作符检查 'pay' 是否在字符串中
                    pipeline_id = item.split(":")[-1]
                    return pipeline_id
        elif len(matched_pipelines) == 1:
            pipeline_id = matched_pipelines[0].split(":")[-1]
            print(pipeline_id)
            return pipeline_id
        else:
            print("没有找到相关的流水线")
    except requests.RequestException as e:
        print(f"Error fetching pipeline ID: {e}")
        return None

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

def Get_Step_Out_puts(project_id, pipeline_id, pipeline_run_id, step_run_ids): # 获取流水线步骤执行输出
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
                                    step_run_id = rule["stepRunId"]

                                    # 假设fact是metricExecutionResults列表中最后一个元素的fact
                                    if 'ruleContents' in rule and rule['ruleContents']:
                                        metric_results = rule['ruleContents'][0].get('metricExecutionResults', [])
                                        if metric_results:
                                            fact = metric_results[-1].get('fact', '未知')
                                            # print(f"失败步骤名称：{rule_name}")
                                            # print(f"stepRunId: {step_run_id}")
                                            # print(f"API测试通过率：{fact}")
                                            return "%s/%s" % (rule_name,fact)
    except requests.RequestException as e:
        print(f"请求错误：{e}")
    except Exception as e:
        print(f"处理错误：{e}")
def create_dingtalk_message(title, pipeline_name, start_time, end_time, pipeline_run_status, ruleContents, server_name_string, url): # 钉钉消息模板定义
    status_color = {
        "COMPLETED": "#32CD32",
        "FAILED": "#FF0000",
        "OTHER": "#FFA500",
        "RUNNING": "#32CD32"
    }
    color = status_color.get(pipeline_run_status, "#FFA500")
    module_dict = {
        "ShenYu网关检查": ["15206115285"],
        "健康检查-fund-server": ["15206115285"],
        "健康检查-Id-server": ["15206115285"],
        "健康检查-Base-server": ["15206115285"],
        "健康检查-amazon-wms": ["15206115285"],
        "海外-shenyu网关健康检查": ["15206115285"],
        "wecom": ["15728046338"],
        "oms": ["15728046338"],
        "anth-server": ["18515343059"],
        "sms-center": ["18515343059"],
        "delivery-server": ["18515343059"],
        "独享-amazonretail": ["15728046338"],
        "独享-pos": ["15728046338"],
        "独享-水星b端": ["15728046338"],
        "独享-水星小程序": ["15728046338"],
        "独享argus": ["15728046338"],
        "独享-amazonCenter-库存": ["18368404677"],
        "独享-amazonWhs": ["18368404677"],
        "独享-amazonCenter-采购": ["18368404677"],
        "独享-amazonCenter-配送": ["18368404677"],
        "user-center": ["18515343059"],
        "amazon-report": ["18515343059"],
        "minipay": ["18515343059"],
        "allpay-web": ["18515343059"],
        "finance-server": ["18515343059"],
        "enivoice": ["18515343059"],
        "wms-标品": ["18368404677"],
        "wms-非标": ["18368404677"],
        "fund-server": ["18368404677"],
    }
    module_name = ruleContents.split("/")[0]
    fate = ruleContents.split("/")[-1]
    if title=="结束":
        if pipeline_run_status=="FAILED":
            notification_phone_list = module_dict.get(module_name, None)
            text = f"### CodeArts Pipeline执行{title}\n\n" \
                   f"> **流水线名称:** {pipeline_name}\n\n" \
                   f"> **开始时间:** {start_time}\n\n" \
                   f"> **结束时间:** {end_time}\n\n" \
                   f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
                   f"> **失败原因:** <font color={color}>{module_name}套件失败，API测试通过率{fate}</font>\n\n" \
                   f"> **链接:** [**查看详情**]({url})\n\n" \
                   f"> **此流水线由{server_name_string}等触发**\n\n" \
                   f"> **自动化测试**  \n\n"
        else:
            notification_phone_list = []
            text = f"### CodeArts Pipeline执行{title}\n\n" \
                   f"> **流水线名称:** {pipeline_name}\n\n" \
                   f"> **开始时间:** {start_time}\n\n" \
                   f"> **结束时间:** {end_time}\n\n" \
                   f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
                   f"> **链接:** [**查看详情**]({url})\n\n" \
                   f"> **此流水线由{server_name_string}等触发**\n\n" \
                   f"> **自动化测试**  \n\n"
    else:
        notification_phone_list = []
        text = f"### CodeArts Pipeline执行{title}\n\n" \
               f"> **工作流名称:** {pipeline_name}\n\n" \
               f"> **开始时间:** {start_time}\n\n" \
               f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
               f"> **工作流链接:** [**查看详情**]({url})\n\n" \
               f"> **此流水线由{server_name_string}等触发**\n\n" \
               f"> **自动化测试** \n\n"

    result = ding_talk.send_markdown(title, text, at_mobiles=notification_phone_list, is_at_all=False)
    if result['errmsg'] == 'ok':
        print('通知成功')
    else:
        print(f'通知失败: {result["errmsg"]}')


# def send_dingtalk_message(webhook_url, message):  # 发送钉钉消息
#     headers = {'Content-Type': 'application/json'}
#     try:
#         response = requests.post(webhook_url, data=json.dumps(message), headers=headers)
#         response.raise_for_status()
#         return response.text
#     except requests.exceptions.RequestException as e:
#         print("Error sending DingTalk message:", e)
#         sys.exit(1)

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
    # webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token=d1b408bc9c147c819da6915baac84ac677c2f3cfbb8d2a8f7530b84e4e4974a8'
    webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token=425ff9a2f17b8143c46a951ad3eba20ff69e9b615fcb7d4b8b5bdf383dd56568'
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
    service_name = args.s
    if pid != 2:
        wait_or_execute(pid)
    else:
        pass
    # 这些需要从外部传入
    task_url = "https://devops.nhsoft.cn/v1/projects/detail/earth-ama/pipelines/custom/ceshihuanjing-bushu/1564?display_name=%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83-%E9%83%A8%E7%BD%B2"
    # 原始时间戳字符串，以毫秒为单位
    start_time_str = '1718939276'
    # 将字符串转换为整数，并除以1000以获得秒级的时间戳
    start_time_int = int(start_time_str)
    # 使用fromtimestamp方法将时间戳转换为datetime对象
    start_time = datetime.fromtimestamp(start_time_int)
    # 将传入的参数进行进一步的处理
    service_name_string = get_string(service_name)

    project_id = "8672d4f0470f4eaf8bd75e2589934d21"
    pipeline_id = get_pipeline_id(project_id, dict_key_string) #通过标签获取pipeline_id，目前正在测试中。。。。
    print(pipeline_id)
    if pipeline_id :
        choose_dict = get_choose_jobs_and_stages_lists(project_id, pipeline_id)
        choose_jobs = choose_dict['choose_jobs']
        choose_stages = choose_dict['choose_stages']
    else:
        title = "失败"
        pipeline_name = "正式环境-更新"
        pipeline_status = "没有对应的标签,请给流水线添加对应的标签"
        end_time = ""
        create_dingtalk_message(title,
                                          pipeline_name,
                                          start_time,
                                          end_time,
                                          pipeline_status,
                                          service_name_string,
                                          task_url)
        sys.exit(1)
    get_pipeline_running_lists(project_id)
    pipeline_run_id = run_pipeline(pipeline_id, project_id, choose_jobs, choose_stages)
    if pipeline_run_id:
        title = "开始"
        workflow_name="正式环境-更新"
        pipeline_status="RUNNING"
        end_time=""
        ruleContents = ""
        create_dingtalk_message(title,
                              workflow_name,
                              start_time,
                              end_time,
                              pipeline_status,
                              ruleContents,
                              service_name_string,
                              task_url)
        pipeline_status = get_pipeline_status(project_id, pipeline_id, pipeline_run_id)
        if pipeline_status:
            title = "结束"
            if pipeline_status['pipeline_run_status']=="FAILED":
                step_run_ids = get_pipeline_step_run_ids(project_id, pipeline_id)
                ruleContents=Get_Step_Out_puts(project_id, pipeline_id, pipeline_run_id, step_run_ids)
                create_dingtalk_message(title,
                                      pipeline_status['pipeline_name'],
                                      pipeline_status['start_time'],
                                      pipeline_status['end_time'],
                                      pipeline_status['pipeline_run_status'],
                                      ruleContents,
                                      service_name_string,
                                      url=f"https://devcloud.cn-east-3.huaweicloud.com/cicd/project/{project_id}/pipeline/detail/{pipeline_id}/{pipeline_run_id}?v=1")
            else:
                ruleContents = ""
                create_dingtalk_message(title,
                                          pipeline_status['pipeline_name'],
                                          pipeline_status['start_time'],
                                          pipeline_status['end_time'],
                                          pipeline_status['pipeline_run_status'],
                                          ruleContents,
                                          service_name_string,
                                          url=f"https://devcloud.cn-east-3.huaweicloud.com/cicd/project/{project_id}/pipeline/detail/{pipeline_id}/{pipeline_run_id}?v=1")
            if pipeline_status['pipeline_run_status'] != "COMPLETED":
                print("Pipeline run did not complete successfully. Exiting.")
                sys.exit(1)
