# -- coding: utf-8 --
from dingtalkchatbot.chatbot import DingtalkChatbot
webhook = 'https://oapi.dingtalk.com/robot/send?access_token=425ff9a2f17b8143c46a951ad3eba20ff69e9b615fcb7d4b8b5bdf383dd56568'
ding_talk = DingtalkChatbot(webhook)

def create_dingtalk_message(title, pipeline_name, start_time, end_time, pipeline_run_status, ruleContents, server_name_string, url): # 钉钉消息模板定义
    status_color = {
        "COMPLETED": "#32CD32",
        "FAILED": "#FF0000",
        "OTHER": "#FFA500",
        "RUNNING": "#32CD32"
    }
    color = status_color.get(pipeline_run_status, "#FFA500")
    if title=="CodeArts Pipeline执行结束":
        if pipeline_run_status=="FAILED":
            text = f"### {title}\n\n" \
                   f"> **流水线名称:** {pipeline_name}\n\n" \
                   f"> **开始时间:** {start_time}\n\n" \
                   f"> **结束时间:** {end_time}\n\n" \
                   f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
                   f"> **失败原因:** <font color={color}>{ruleContents}</font>\n\n" \
                   f"> **链接:** [**查看详情**]({url})\n\n" \
                   f"> **此流水线由{server_name_string}等触发**\n\n" \
                   f"> **自动化测试**  \n\n"
        else:
            text = f"### CodeArts Pipeline执行{title}\n\n" \
                   f"> **流水线名称:** {pipeline_name}\n\n" \
                   f"> **开始时间:** {start_time}\n\n" \
                   f"> **结束时间:** {end_time}\n\n" \
                   f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
                   f"> **链接:** [**查看详情**]({url})\n\n" \
                   f"> **此流水线由{server_name_string}等触发**\n\n" \
                   f"> **自动化测试**  \n\n"
    else:
        text = f"### {title}\n\n" \
               f"> **工作流名称:** {pipeline_name}\n\n" \
               f"> **开始时间:** {start_time}\n\n" \
               f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
               f"> **工作流链接:** [**查看详情**]({url})\n\n" \
               f"> **此流水线由{server_name_string}等触发**\n\n" \
               f"> **自动化测试**  \n\n"

    notification_phone_list=["17612843195"]
    # notification_phone_list=[]
    result = ding_talk.send_markdown(title, text, at_mobiles=notification_phone_list, is_at_all=False)
    if result['errmsg'] == 'ok':
        print('通知成功')
    else:
        print(f'通知失败: {result["errmsg"]}')
if __name__ == '__main__':
    title = "CodeArts Pipeline执行结束"
    pipeline_name="test"
    start_time=""
    end_time=""
    pipeline_run_status="FAILED"
    ruleContents="dsfsdfsfddsfs"
    server_name_string="xxxxxx"
    url="https://oapi.dingtalk.com"
    create_dingtalk_message(title, pipeline_name, start_time, end_time, pipeline_run_status, ruleContents, server_name_string, url)
