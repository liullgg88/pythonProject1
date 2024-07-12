import json

# 从JSON文件中读取数据
with open('data_file.json', 'r', encoding='utf-8') as file:
    loaded_data = json.load(file)

# 打印读取到的数据
# print(loaded_data)

# 访问特定键的数据并解析其JSON字符串值
sy_data_string = loaded_data['sy']
data = json.loads(sy_data_string)
print(data)