import requests
import os
class shenyu:
    def __init__(self):
        self.dev = {"url":"sy-g-admin-dev.nhsoft.cn","password":"Lemonxxx","username":"admin","enviroment":"dev"}                       # 测试环境
        self.prod_shared = {"url":"earth-shenyu.lemeng.center","password":"Nhsoftxxx","username":"admin","enviroment":"prod_shared"}        # 独享集群
        self.prod_unique = {"url":"shenyu-admin-dx.lemeng.center","password":"Nhsoftxxx","username":"admin","enviroment":"prod_unique"}     # 共享集群
        self.prod_lshm = {"url":"shenyu-admin.hnlshm.com","password":"Nhsoftxxxx","username":"admin","enviroment":"prod_lshm"}                   # 零食很忙集群
        self.customer = ""
        self.Intra_Domain_Name = ""
        self.app = {
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
    def login(self,source):
        """
        登录到指定的系统并返回访问令牌。
        Args:
            username (str): 用户名。
            password (str): 密码。
        Returns:
            str: 访问令牌，如果登录失败则返回 None。
        """
        url = f"https://{source["url"]}/platform/login"
        params = {"userName": source["username"], "password": source["password"]}
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

    def create_selector(self, token, env, order):
        """
        使用指定的访问令牌创建选择器。
        Args:
            token (str): 访问令牌。
        """
        url = f"https://{env["url"]}/selector"
        # 环境名称tag大写化,例如als则为ALS
        tag = self.customer.split("-")[0].upper()
        for server_name in self.app:
            selector_name = f"{tag}-{server_name}"  # 构建选择器名称
            service_name=self.app[server_name]
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
                "sort": order+1,

                "handle": "[{\"upstreamUrl\":\"%s-%s-svc.%s-node-dx.svc.cluster.local:80\",\"weight\":\"100\",\"timestamp\":0,\"warmup\":0,\"status\":true}]" % (env["enviroment"]
                ,service_name,env["enviroment"]),
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
    def get_data_info(self,token,env):
        url1 = f"https://{env["url"]}/selector?pluginId=5&currentPage=1&pageSize=1000"
        url2 = f"https://{env["url"]}/selector?currentPage=1&pageSize=1000&pluginId=26"
        headers = {
            "X-Access-Token": token,
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url1, headers=headers)
            response.raise_for_status()  # 如果请求失败（例如，404、500等），则引发HTTPError异常
            data_divide_list = response.json()["data"]['dataList']
            response = requests.get(url2, headers=headers)
            response.raise_for_status()  # 如果请求失败（例如，404、500等），则引发HTTPError异常
            data_websocket_list = response.json()["data"]['dataList']
            if not data_websocket_list or not data_divide_list:
                print("No data found in the response.")
                return None

            # 获取资源列表
            data_divide_info = [(i['sort'], i["name"]) for i in data_divide_list]
            data_websocket_info = [(i['sort'], i["name"]) for i in data_websocket_list]
            return data_divide_info,data_websocket_info


        except (requests.exceptions.RequestException, KeyError, ValueError) as e:
            print(f"An error occurred: {e}")
            return None

    def create_websocketr(self,token, env, order, ):
        """
        使用指定的访问令牌创建选择器。
        Args:
            token (str): 访问令牌。
        """
        url = f"https://{env["url"]}/selector"
        headers = {
            "X-Access-Token": token,
            "Content-Type": "application/json"
        }
        # 第一条argus的WebSocket规则的body
        body1 = {
            "pluginId": "26",
            "name": "%s-arguswebsocket选择器" % self.customer,
            "type": 1,
            "matchMode": "0",
            "continued": False,
            "loged": False,
            "enabled": True,
            "matchRestful": False,
            "sort": order+1,
            "handle": "[{\"url\":\"%s\",\"weight\":\"100\",\"timestamp\":0,\"warmup\":0,\"status\":true}]" % self.Intra_Domain_Name,
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
                    "paramValue": "%s" % self.customer.upper()
                }
            ]
        }
        # 第二条mercury-server-v2的WebSocket规则的body
        body2 = {
            "pluginId": "26",
            "name": "%s-mercury-server-v2websocket" % self.customer,  # 修改名称以区分规则
            "type": 1,
            "matchMode": "0",
            "continued": False,
            "loged": False,
            "enabled": True,
            "matchRestful": False,
            "sort":  order+1,
            "handle": "[{\"url\":\"%s\",\"weight\":\"100\",\"timestamp\":0,\"warmup\":0,\"status\":true}]" % self.Intra_Domain_Name,
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
                    "paramValue": "%s" % self.customer.upper()
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

    ###各客户需要批量添加单个应用时调用
    def create_all_customer_selector(self, env, server_name):
        """
         使用指定的访问令牌创建选择器。
         Args:
             token (str): 访问令牌。
         """
        # print(env)
        token = self.login(env)
        url = f"https://{env["url"]}/selector"
        data_divide_info = self.get_data_info(token,env)
        costumer_list = []
        for i in data_divide_info[0]:
            if (i[0],i[1].split("-")[0].upper()) not in costumer_list:
                costumer_list.append((i[0],i[1].split("-")[0].upper()))
        for i in costumer_list:
            order = i[0]
            tag = i[1].split("-")[0].upper()
            # 构建选择器名称
            selector_name = f"{i[1].split("-")[0].upper()}-{server_name}"
            body = {
                "pluginId": "5",
                "name": "%s" % selector_name,
                "type": 1,
                "matchMode": "0",
                "continued": False,
                "loged": False,
                "enabled": True,
                "matchRestful": False,
                "sort": order,

                "handle": "[{\"upstreamUrl\":\"%s-%s-svc.%s-node-dx.svc.cluster.local:80\",\"weight\":\"100\",\"timestamp\":0,\"warmup\":0,\"status\":true}]" % (
                    env["enviroment"], server_name, env["enviroment"]),
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
            headers = {
                "X-Access-Token": token,
                "Content-Type": "application/json"
            }
            try:
                response = requests.post(url, json=body, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    print(f"{tag}-{server_name}选择器创建成功！")
                    # 这里可以根据需要处理响应数据
                else:
                    print("创建选择器请求失败！状态码:", response.status_code)
            except Exception as e:
                print("创建选择器请求发生异常:", e)

if __name__ == "__main__":
    # # 不再从环境变量中获取，而是手动输入
    shenyu = shenyu()
    environment = input("请输入环境名称（dev, prod_shared, prod_unique, prod_lshm）: ")
    source = shenyu.__dict__
    if environment not in source.keys():
        raise ValueError(f"Unknown environment: {environment}")
    token = shenyu.login(source[environment])
    data_info = shenyu.get_data_info(token,source[environment])
    shenyu.customer = input(
        "请输入客户名称首字母小写（例如：爱零食的首字母小写als）: ").strip().lower()  # 客户名称,例如 “爱零食的首字母小写als“
    divide_order = max([i[0] for i in data_info[0]])  # 获取divide的sort值里面最大的值
    shenyu.Intra_Domain_Name = input("请输入argus服务的内网域名（例如：intranet.example.local  ）: ").strip()
    websocket_order = max([i[0] for i in data_info[1]])  # 获取websocket的sort值里面最大的值
    if token:
        shenyu.create_selector(token,source[environment],divide_order)