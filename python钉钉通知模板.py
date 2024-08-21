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
    #手机号对应关系：相庆华：15206115285，陈丽：15728046338，黄华园:18515343059,周丽霞:18368404677,
    module_dict={
        "ShenYu网关检查":["15206115285"],
        "健康检查-fund-server":["15206115285"],
        "健康检查-Id-server":["15206115285"],
        "健康检查-Base-server":["15206115285"],
        "健康检查-amazon-wms":["15206115285"],
        "海外-shenyu网关健康检查": ["15206115285"],
        "wecom":["15728046338"],
        "oms":["15728046338"],
        "anth-server":["18515343059"],
        "sms-center":["18515343059"],
        "delivery-server":["18515343059"],
        "独享-amazonretail":["15728046338"],
        "独享-pos":["15728046338"],
        "独享-水星b端":["15728046338"],
        "独享-水星小程序":["15728046338"],
        "独享argus":["15728046338"],
        "独享-amazonCenter-库存":["18368404677"],
        "独享-amazonWhs":["18368404677"],
        "独享-amazonCenter-采购":["18368404677"],
        "独享-amazonCenter-配送":["18368404677"],
        "user-center":["18515343059"],
        "amazon-report":["18515343059"],
        "minipay":["18515343059"],
        "allpay-web":["18515343059"],
        "finance-server":["18515343059"],
        "enivoice":["18515343059"],
        "wms-标品":["18368404677"],
        "wms-非标":["18368404677"],
        "fund-server":["18368404677"],
    }
    module_name = ruleContents.split("/")[0]
    fate=ruleContents.split("/")[-1]

    if title=="CodeArts Pipeline执行结束":
        if pipeline_run_status=="FAILED":
            notification_phone_list = module_dict.get(module_name,None)
            text = f"### {title}\n\n" \
                   f"> **流水线名称:** {pipeline_name}\n\n" \
                   f"> **开始时间:** {start_time}\n\n" \
                   f"> **结束时间:** {end_time}\n\n" \
                   f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
                   f"> **运行状态:** <font color={color}>{module_name}套件失败，API测试通过率{fate}</font>\n\n" \
                   f"> **链接:** [**查看详情**]({url})\n\n" \
                   f"> **此流水线由{server_name_string}等触发**\n\n" \
                   f"> **自动化测试**  \n\n"
        else:
            notification_phone_list=[]
            text = f"### CodeArts Pipeline执行{title}\n\n" \
                   f"> **流水线名称:** {pipeline_name}\n\n" \
                   f"> **开始时间:** {start_time}\n\n" \
                   f"> **结束时间:** {end_time}\n\n" \
                   f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
                   f"> **链接:** [**查看详情**]({url})\n\n" \
                   f"> **此流水线由{server_name_string}等触发**\n\n" \
                   f"> **自动化测试**  \n\n"
    else:
        notification_phone_list=[]
        text = f"### {title}\n\n" \
               f"> **工作流名称:** {pipeline_name}\n\n" \
               f"> **开始时间:** {start_time}\n\n" \
               f"> **运行状态:** <font color={color}>{pipeline_run_status}</font>\n\n" \
               f"> **工作流链接:** [**查看详情**]({url})\n\n" \
               f"> **此流水线由{server_name_string}等触发**\n\n" \
               f"> **自动化测试**  \n\n"

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
    ruleContents="wms-标品/0.2778"
    server_name_string="xxxxxx"
    url="https://oapi.dingtalk.com"
    create_dingtalk_message(title, pipeline_name, start_time, end_time, pipeline_run_status, ruleContents, server_name_string, url)
