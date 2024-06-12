import requests


def login(username, password):
    """
    登录到指定的系统并返回访问令牌。
    Args:
        username (str): 用户名。
        password (str): 密码。
    Returns:
        str: 访问令牌，如果登录失败则返回 None。
    """
    url = "https://sy-g-admin-dev.nhsoft.cn/platform/login"
    # 生产环境url
    # url = "https://shenyu-admin-dx.lemeng.center/platform/login"
    params = {"userName": username, "password": password}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["code"] == 200:
                token = data["data"]["token"]
                print("登录成功！Token:", token)
                return token
            else:
                print("登录失败:", data["message"])
        else:
            print("登录请求失败！状态码:", response.status_code)
    except Exception as e:
        print("登录请求发生异常:", e)
    return None


def create_selector(token, server_name, service_Env_Name, service_Env_ID):
    """
    使用指定的访问令牌创建选择器。
    Args:
        token (str): 访问令牌。
    """
    url = "https://sy-g-admin-dev.nhsoft.cn/selector"
    # 生产环境url
    # url = "https://shenyu-admin-dx.lemeng.center/selector"
    # 环境名称tag大写化,例如als则为ALS
    tag = service_Env_Name.split("-")[0].upper()
    selector_name = f"{tag}-{server_name}"  # 构建选择器名称
    amazon_dict = {
        "amazon-retail": "amazon-retail",
        "amazon-wms": "amazonwms",
        "amazon-base": "amazon-base",
        "amazon-retail-pos": "amazon-retail",
        "amazon-center": "erp-amazoncenter",
        "amazon-pos": "pos-amazoncenter",
        "amazon-report": "amazonreport",
        "argus": "argus",
        "base-server": "base-server",
        "fund-server": "fund-server",
        "mercury-server-v2": "merv2-server",
        "amazonCenter": "pos-amazoncenter",
        "user-center-v2": "usercenter",
        "amazon-whs": "amazonwhsserver"
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
        "sort": service_Env_ID, #LYP-amazon-retail-production-svc.LYP-node-dx.svc.cluster.local:80

        "handle": "[{\"upstreamUrl\":\"%s-%s-production-svc.%s-node-dx.svc.cluster.local:80\",\"weight\":\"100\",\"timestamp\":0,\"warmup\":0,\"status\":true}]" % (service_Env_Name
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


if __name__ == "__main__":
    username = "admin"
    password = "Nhsoft_123"
    token = login(username, password)
    Env_Name = input("请输入客户环境名称(小写字母): ").strip()
    Env_ID = input("请输入一个数字，确保shenyu-admin中Divide Order数值唯一: ").strip()
    service_data = {
        server: {
            "env_name": Env_Name,
            "env_id": Env_ID,
    } for server in ['amazon-retail', 'amazon-wms', 'amazon-base', 'amazon-retail-pos', 'amazon-center', 'amazon-pos', 'amazon-report', 'argus', 'base-server', 'fund-server', 'mercury-server-v2', 'amazonCenter', 'amazon-whs', "user-center-v2"]
    #     } for server in ["service1", "service2", "service3"]
    }
    if token:
        for server_name, info in service_data.items():
            service_Env_Name = info.get("env_name")
            service_Env_ID = info.get("env_id")
            if service_Env_Name and service_Env_ID:
                create_selector(token, server_name, service_Env_Name, service_Env_ID)
            else:
                print(f"Missing environment data for service '{server_name}'.")

