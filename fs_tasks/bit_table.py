import requests
import yaml
import time

with open("FS_KEY.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def get_table_items(access_token, url, field_names: list):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {"page_size": 500}
    if field_names:
        data = {"fields": field_names}
    page_token = None
    while True:
        if page_token:
            params["page_token"] = page_token
        response = requests.post(url, headers=headers, params=params, json=data)
        if response.status_code != 200:
            print(response.text)
            break
        result = response.json()
        if result["code"] != 0:
            print(response.text)
            break
        for item in result["data"]["items"]:
            yield item
        if not result["data"]["has_more"]:
            break
        page_token = result["data"]["page_token"]


def get_projects_items(access_token, field_names: list):
    url = "https://open.feishu.cn/open-apis/bitable/v1/apps/{}/tables/{}/records/search".format(
        config["BIT_TABLE_APP_TOKEN"], config["PROJECTS_TABLE_ID"]
    )
    return list(get_table_items(access_token, url, field_names))


def get_tasks_items(access_token, field_names: list):
    url = "https://open.feishu.cn/open-apis/bitable/v1/apps/{}/tables/{}/records/search".format(
        config["BIT_TABLE_APP_TOKEN"], config["TASKS_TABLE_ID"]
    )
    return list(get_table_items(access_token, url, field_names))


def get_daily_items(access_token, field_names: list):
    url = "https://open.feishu.cn/open-apis/bitable/v1/apps/{}/tables/{}/records/search".format(
        config["BIT_TABLE_APP_TOKEN"], config["DAILY_TABLE_ID"]
    )
    return list(get_table_items(access_token, url, field_names))


def get_tasks_by_user(access_token, user_id):
    task_list = get_tasks_items(
        access_token, ["任务", "优先级", "状态", "开始时间", "截止时间", "任务执行人"]
    )
    task_name_list = []
    task_priority_list = []
    end_date_list = []
    for task in task_list:
        try:
            if task["fields"]["状态"] not in ["进行中", "未开始"]:
                continue
            if task["fields"]["开始时间"] > int(time.time() * 1000):
                continue
            for user in task["fields"]["任务执行人"]:
                if user["id"] != user_id:
                    continue
                task_name_list.append(task["fields"]["任务"][0]["text"])
                task_priority_list.append(task["fields"]["优先级"])
                end_date_list.append(task["fields"]["截止时间"])
                break
        except:
            continue
    return task_name_list, task_priority_list, end_date_list
