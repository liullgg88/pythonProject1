import re

# 测试字符串
test_strings = ["这是一个汉字字符串", "EnglishOnly", "数字123和汉字混合", "😀表情符号不含汉字", "表情😀后跟汉字开始"]

# 编译正则表达式，匹配包含至少一个汉字的字符串
pattern = re.compile(r'^[\u4e00-\u9fa5]')

# 遍历测试字符串并检查
for s in test_strings:
    if pattern.search(s):
        print(f"'{s}' 以汉字开头。")
    else:
        print(f"'{s}' 不以汉字开头。")