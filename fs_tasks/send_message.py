import requests
import json
import time
import random


def get_good_morning_message():
    with open("fs_tasks/good_morning.txt", "r", encoding="utf-8") as f:
        morning_lines = f.readlines()
    random_line = random.choice(morning_lines)
    return random_line


def send_message_p2p(access_token, data):
    url = "	https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {
        "receive_id_type": "open_id",
    }
    requests.post(url, headers=headers, params=params, json=data)


def send_message_group(access_token, data):
    url = "	https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {
        "receive_id_type": "chat_id",
    }
    requests.post(url, headers=headers, params=params, json=data)


def send_text_message(access_token, target_id, text, chat_type="p2p"):
    content = {
        "text": text,
    }
    data = {
        "receive_id": target_id,
        "msg_type": "text",
        "content": json.dumps(content),
    }
    if chat_type == "group":
        send_message_group(access_token, data)
    else:
        send_message_p2p(access_token, data)


def send_post_message(access_token, target_id, content, chat_type="p2p"):
    data = {
        "receive_id": target_id,
        "msg_type": "post",
        "content": json.dumps(content),
    }
    if chat_type == "group":
        send_message_group(access_token, data)
    else:
        send_message_p2p(access_token, data)


def send_create_project_message(
    access_token,
    user_id,
    project_name,
    project_content,
    end_date,
    create_user_id,
    project_status,
):
    end_date_str = time.strftime("%Y-%m-%d", time.localtime(int(end_date) / 1000))
    content = {
        "type": "template",
        "data": {
            "template_id": "AAq7VZ8RNpmlV",
            "template_variable": {
                "project_name": project_name,
                "project_content": project_content,
                "end_date": end_date_str,
                "create_user_id": create_user_id,
                "project_status": project_status,
            },
        },
    }
    data = {
        "receive_id": user_id,
        "msg_type": "interactive",
        "content": json.dumps(content),
    }
    send_message_p2p(access_token, data)


def send_daily_remainder(
    access_token,
    user_id,
    task_name_list,
    task_priority_list,
    end_date_list,
):
    priority_color = {
        "P0": "red",
        "P1": "orange",
        "P2": "yellow",
        "P3": "gray",
    }
    task_table_data = []
    for i in range(len(task_name_list)):
        task_table_data.append(
            {
                "task_name": task_name_list[i],
                "task_priority": [
                    {
                        "text": task_priority_list[i],
                        "color": priority_color[task_priority_list[i]],
                    }
                ],
                "end_date": int(end_date_list[i]),
            }
        )
    with open("fs_tasks/card_json/daily_remainder.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
    json_data["i18n_elements"]["zh_cn"][2]["rows"] = task_table_data
    json_data["i18n_elements"]["zh_cn"][0]["content"] = get_good_morning_message()
    data = {
        "receive_id": user_id,
        "msg_type": "interactive",
        "content": json.dumps(json_data),
    }
    send_message_p2p(access_token, data)

def send_task_remainder(
    access_token,
    user_id,
    task_name_list,
    task_priority_list,
    end_date_list,
):
    priority_color = {
        "P0": "red",
        "P1": "orange",
        "P2": "yellow",
        "P3": "gray",
    }
    task_table_data = []
    for i in range(len(task_name_list)):
        task_table_data.append(
            {
                "task_name": task_name_list[i],
                "task_priority": [
                    {
                        "text": task_priority_list[i],
                        "color": priority_color[task_priority_list[i]],
                    }
                ],
                "end_date": int(end_date_list[i]),
            }
        )
    with open("fs_tasks/card_json/task_remainder.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
    json_data["i18n_elements"]["zh_cn"][0]["rows"] = task_table_data
    data = {
        "receive_id": user_id,
        "msg_type": "interactive",
        "content": json.dumps(json_data),
    }
    send_message_p2p(access_token, data)


def send_daily_remainder_no_task(access_token, user_id):
    content = {
        "type": "template",
        "data": {
            "template_id": "AAq7kY7GQIh2p",
        },
    }
    data = {
        "receive_id": user_id,
        "msg_type": "interactive",
        "content": json.dumps(content),
    }
    send_message_p2p(access_token, data)


def send_daily_report_link(access_token, target_id, chat_type="p2p"):
    content = {
        "type": "template",
        "data": {
            "template_id": "AAq7H6eapCzVc",
        },
    }
    data = {
        "receive_id": target_id,
        "msg_type": "interactive",
        "content": json.dumps(content),
    }
    if chat_type == "group":
        send_message_group(access_token, data)
    else:
        send_message_p2p(access_token, data)


def send_off_duty_reminder(access_token, user_id):
    content = {
        "type": "template",
        "data": {
            "template_id": "AAq7HXNXebttn",
        },
    }
    data = {
        "receive_id": user_id,
        "msg_type": "interactive",
        "content": json.dumps(content),
    }
    send_message_p2p(access_token, data)
