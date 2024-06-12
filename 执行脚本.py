import json

# 包含多个键值对的字典，每个值都是一个JSON字符串
test_mapping = {
    "retail-lll": '{"pipeline_id": "d7580ec1f3ab4f7bae2028c8bd5c66cd", "choose_jobs": "168864794392314618d37-850e-46c8-b911-d2d644b19430", "choose_stages": 0}',
    "retail-mmm": '{"pipeline_id": "another_id", "choose_jobs": "another_job_id", "choose_stages": 1}',
    "retail-nnn": '{"pipeline_id": "third_id", "choose_jobs": "third_job_id", "choose_stages": 2}',
    # 可以继续添加更多键值对...
}
x=test_mapping["retail-lll"]
data = '{\"pipeline_id\": \"d7580ec1f3ab4f7bae2028c8bd5c66cd\", \"choose_jobs\": \"168864794392314618d37-850e-46c8-b911-d2d644b19430\", \"choose_stages\": 0}'


