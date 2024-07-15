import requests
import os
import configparser


def login(username, password, url):
    """
    登录到指定的系统并返回访问令牌。
    Args:
        username (str): 用户名。
        password (str): 密码。
    Returns:
        str: 访问令牌，如果登录失败则返回 None。
    """
    url = f"https://{url}/platform/login"
    # url = "https://sy-g-admin-dev.nhsoft.cn/platform/login"
    # 生产环境url
    # url = "https://earth-shenyu.lemeng.center/platform/login"
    # url = "https://shenyu-admin-dx.lemeng.center/platform/login"
    # 生产环境零食很忙集群的shenyu-admin地址
    # url = "https://shenyu-admin.hnlshm.com/platform/login"
    params = {"userName": username, "password": password}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["code"] == 200:
                token = data["data"]["token"]
                # print("登录成功！Token:", token)
                return token
            else:
                print("登录失败:", data["message"])
        else:
            print("登录请求失败！状态码:", response.status_code)
    except Exception as e:
        print("登录请求发生异常:", e)
    return None

def create_selector(token, server_name, service_Env_Name, service_Env_ID, url):
    """
    使用指定的访问令牌创建选择器。
    Args:
        token (str): 访问令牌。
    """
    url = f"https://{url}/selector"
    # url = "https://sy-g-admin-dev.nhsoft.cn/selector"
    # 生产环境共享集群的shenyu-admin url
    # url = "https://earth-shenyu.lemeng.center/selector"
    # 生产环境独享集群的shenyu-admin url
    # url = "https://shenyu-admin-dx.lemeng.center/selector"
    # 生产环境零食很忙集群的shenyu-admin地址
    # url = "https://shenyu-admin.hnlshm.com/selector"
    # 环境名称tag大写化,例如als则为ALS
    tag = service_Env_Name.split("-")[0].upper()
    selector_name = f"{tag}-{server_name}"  # 构建选择器名称
    amazon_dict = {
        "amazon-retail": "amazon-retail",
        "amazon-wms": "amazonwms",
        "amazon-base": "amazon-base",
        "amazon-retail-pos": "amazon-retail",
        "amazon-center": "erp-amazon-center",
        "amazon-pos": "pos-amazon-center",
        "amazon-report": "amazon-report",
        "argus": "argus",
        "fund-server": "fund-server",
        "mercury-server-v2": "merv2-server",
        "amazonCenter": "pos-amazoncenter",
        "user-center-v2": "user-center",
        "amazon-whs": "amazon-whs-server"
    }
    service_name=amazon_dict[server_name]
    headers = {
        "X-Access-Token": token,
        "Content-Type": "application/json"
    }
    body = {
        "pluginId": "5",
        "name": "%s" %  selector_name,
        "type": 1,
        "matchMode": "0",
        "continued": False,
        "loged": False,
        "enabled": True,
        "matchRestful": False,
        "sort": service_Env_ID+1,

        "handle": "[{\"upstreamUrl\":\"%s-%s-svc.%s-node-dx.svc.cluster.local:80\",\"weight\":\"100\",\"timestamp\":0,\"warmup\":0,\"status\":true}]" % (service_Env_Name
        ,service_name,service_Env_Name),
        "selectorConditions": [
            {
                "paramType": "uri",
                "operator": "pathPattern",
                "paramName": "/",
                "paramValue": "/%s/**" % server_name
            },
            {
                "paramType": "header",
                "operator": "=",
                "paramName": "x-environment",
                "paramValue": "%s" % tag
            }
        ]
    }
    try:
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("选择器创建成功！")
            # 这里可以根据需要处理响应数据
        else:
            print("创建选择器请求失败！状态码:", response.status_code)
    except Exception as e:
        print("创建选择器请求发生异常:", e)

def get_sort(token , url, pluginId):
    # 测试环境测试集群shenyu-admin url
    url = f"https://{url}/selector?pluginId={pluginId}&currentPage=1&pageSize=1000"
    # https://shenyu-admin.hnlshm.com/selector?currentPage=1&pageSize=12&pluginId=26
    # url = "https://sy-g-admin-dev.nhsoft.cn/selector?pluginId=5&currentPage=1&pageSize=1000"
    # 生产环境独享集群shenyu-admin url
    # url = "https://shenyu-admin-dx.lemeng.center/selector?currentPage=1&pageSize=1000&pluginId=5"
    # 生产环境共享集群shenyu-admin url
    # url = "https://earth-shenyu.lemeng.center/selector?currentPage=1&pageSize=1000&pluginId=5"

    headers = {
        "X-Access-Token": token,
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果请求失败（例如，404、500等），则引发HTTPError异常
        data_list = response.json()["data"]['dataList']
        if not data_list:
            print("No data found in the response.")
            return None

        # 提取sort字段并找到最大值
        sort_values = [i['sort'] for i in data_list]
        max_sort = max(sort_values)
        # max_sort=1
        return max_sort

    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        print(f"An error occurred: {e}")
        return None

def create_websocketr(token, Env_Name, order, Intra_Domain_Name, url):
    """
    使用指定的访问令牌创建选择器。
    Args:
        token (str): 访问令牌。
    """
    url = f"https://{url}/selector"
    headers = {
        "X-Access-Token": token,
        "Content-Type": "application/json"
    }
    # 第一条argus的WebSocket规则的body
    body1 = {
        "pluginId": "26",
        "name": "%s-arguswebsocket选择器" % Env_Name,
        "type": 1,
        "matchMode": "0",
        "continued": False,
        "loged": False,
        "enabled": True,
        "matchRestful": False,
        "sort": order+1,
        "handle": "[{\"url\":\"%s\",\"weight\":\"100\",\"timestamp\":0,\"warmup\":0,\"status\":true}]" % Intra_Domain_Name,
        "selectorConditions": [
            {
                "paramType": "uri",
                "operator": "pathPattern",
                "paramName": "/",
                "paramValue": "/argus/**"
            },
            {
                "paramType": "header",
                "operator": "=",
                "paramName": "x-environment",
                "paramValue": "%s" % Env_Name.upper()
            }
        ]
    }
    # 第二条mercury-server-v2的WebSocket规则的body
    body2 = {
        "pluginId": "26",
        "name": "%s-mercury-server-v2websocket" % Env_Name,  # 修改名称以区分规则
        "type": 1,
        "matchMode": "0",
        "continued": False,
        "loged": False,
        "enabled": True,
        "matchRestful": False,
        "sort":  order+1,
        "handle": "[{\"url\":\"%s\",\"weight\":\"100\",\"timestamp\":0,\"warmup\":0,\"status\":true}]" % Intra_Domain_Name,
        "selectorConditions": [
            {
                "paramType": "uri",
                "operator": "pathPattern",
                "paramName": "/",
                "paramValue": "/mercury-server-v2/nhsoft.mercury.websocket.notify"
            },
            {
                "paramType": "header",
                "operator": "=",
                "paramName": "x-environment",
                "paramValue": "%s" % Env_Name.upper()
            }
        ]
    }
    try:
        # 第一次调用，添加第一条websocket规则
        response1 = requests.post(url, json=body1, headers=headers)
        if response1.status_code == 200:
            print("第一条websocket规则添加成功！")
        else:
            print("添加第一条websocket规则失败！状态码:", response1.status_code)

        # 第二次调用，添加第二条websocket规则（确保body不同）
        response2 = requests.post(url, json=body2, headers=headers)
        if response2.status_code == 200:
            print("第二条websocket规则添加成功！")
        else:
            print("添加第二条websocket规则失败！状态码:", response2.status_code)
    except Exception as e:
        print("添加websocket规则请求发生异常:", e)

if __name__ == "__main__":
    # 不再从环境变量中获取，而是手动输入
    environment = input("请输入环境名称（dev, prod_shared, prod_unique, prod_lshm）: ")
    # 根据输入的环境名称设置URL
    if environment == "dev":
        url = "sy-g-admin-dev.nhsoft.cn"
    elif environment == "prod_shared":
        url = "earth-shenyu.lemeng.center"
    elif environment == "prod_unique":
        url = "shenyu-admin-dx.lemeng.center"
    elif environment == "prod_lshm":
        url = "shenyu-admin.hnlshm.com"
    else:
        raise ValueError(f"Unknown environment: {environment}")
    # shenyu-admin登录用户
    username = "admin"
    #读取密码文件
    config = configparser.ConfigParser()
    config.read('shenyu-admin.ini')
    # 根据环境变量选择密码
    if environment == "dev":
        password = config['Password']['DEV_PASSWORD']
    elif environment == "prod_lshm":
        password = config['Password']['PROD_LSHM_PASSWORD']
    else:
        # 假设'default'、'shared'、'dedicated'或其他任何非特定值都使用共享和独享集群的密码
        password = config['Password']['SHARED_OR_DEDICATED_PASSWORD']  # 提供一个默认值以防万一

    token = login(username, password, url)
    Env_Name = input("请输入客户名称首字母小写（例如：爱零食的首字母小写als）: ").strip().lower()  # 客户名称,例如 “爱零食的首字母小写als“
    Env_ID = get_sort(token, url,5) # 获取divide的sort值里面最大的值
    Intra_Domain_Name = input("请输入argus服务和mercury-server-v2服务的内网域名（例如：intranet.example.local  ）: ").strip()
    websocket_order = get_sort(token, url,26)  # 获取websocket的sort值里面最大的值
    create_websocketr(token, Env_Name, websocket_order, Intra_Domain_Name, url)
    service_data = {
        server: {
            "env_name": Env_Name,
            "env_id": Env_ID,
    # 需要添加的服务名称列表
    } for server in ['amazon-retail', 'amazon-wms', 'amazon-base', 'amazon-retail-pos', 'amazon-center', 'amazon-pos', 'amazon-report', 'argus', 'fund-server', 'mercury-server-v2', 'amazonCenter', 'amazon-whs', "user-center-v2"]

    }
    if token:
        for server_name, info in service_data.items():
            service_Env_Name = info.get("env_name")
            service_Env_ID = info.get("env_id")
            if service_Env_Name and service_Env_ID:
                create_selector(token, server_name, service_Env_Name, service_Env_ID, url)
            else:
                print(f"Missing environment data for service '{server_name}'.")