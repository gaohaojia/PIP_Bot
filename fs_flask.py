from flask import Flask, request, jsonify
import hashlib
import os
import json
import yaml
import queue

from fs_tasks import (
    send_daily_report_link,
    send_text_message,
    send_post_message,
    send_off_duty_reminder,
    get_tasks_by_user,
    send_task_remainder,
    send_daily_remainder_no_task,
    send_check_in_message,
    send_check_out_message,
)
from fs_id import AccessTokenClass, update_user_id_list, convert_employee_id_to_user_id

with open("FS_KEY.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

access_token = AccessTokenClass()


class EventRecorder:
    def __init__(self):
        self._event_queue = queue.Queue(1000)

    def record_event(self, event_id):
        if self._event_queue.full():
            self._event_queue.get(timeout=1)
        self._event_queue.put(event_id)

    def check_event(self, event_id):
        return event_id in self._event_queue.queue


event_recorder = EventRecorder()

app = Flask(__name__)


@app.route("/", methods=["POST"])
def callback_event_handler():
    req_data = request.get_json()
    if req_data.get("schema") is not None:
        return handle_v2(req_data)
    else:
        return handle_v1(req_data)


def handle_v1(req_data):
    # 处理v1版本的回调事件
    if req_data.get("token") != config["VERIFICATION_TOKEN"]:
        return jsonify({"error": "Invalid verification token"}), 403

    if req_data.get("type") == "url_verification":
        return jsonify({"challenge": req_data.get("challenge")})

    return jsonify({"error": "Invalid request"}), 400


def handle_v2(req_data):
    # 处理v2版本的回调事件
    req_header = req_data.get("header")
    if req_header.get("token") != config["VERIFICATION_TOKEN"]:
        return jsonify({"error": "Invalid verification token"}), 403

    if event_recorder.check_event(req_header.get("event_id")):
        return jsonify({"success": True})

    if req_header.get("event_type") == "im.message.receive_v1":
        handle_message_event(req_data.get("event"))
        event_recorder.record_event(req_header.get("event_id"))
        return jsonify({"success": True})

    if req_header.get("event_type") == "drive.file.bitable_record_changed_v1":
        handle_bitable_event(req_data.get("event"))
        event_recorder.record_event(req_header.get("event_id"))
        return jsonify({"success": True})

    if req_header.get("event_type") == "attendance.user_flow.created_v1":
        handle_attendance_event(req_data.get("event"))
        event_recorder.record_event(req_header.get("event_id"))
        return jsonify({"success": True})
    print(req_data)
    return jsonify({"error": "Invalid request"}), 400


def handle_message_event(event):
    # 处理接收到的消息事件
    user_id = event.get("sender").get("sender_id").get("open_id")
    message = event.get("message")
    if message.get("chat_type") == "p2p":
        target_id = user_id
    elif message.get("chat_type") == "group":
        target_id = message.get("chat_id")
    if message.get("message_type") == "text":
        if user_id == config["MANAGER_USER_ID"]:
            if handle_advanced_permission_event(message):
                return
        text_content: str = json.loads(message.get("content")).get("text")
        if text_content.find("日报") != -1 or text_content.find("daily report") != -1:
            send_daily_report_link(access_token(), target_id, message.get("chat_type"))
            return
        if (
            text_content.find("任务") != -1 or text_content.find("task") != -1
        ) and message.get("chat_type") == "p2p":
            task_name_list, task_priority_list, end_date_list = get_tasks_by_user(
                access_token(), user_id
            )
            if len(task_name_list) > 0:
                send_task_remainder(
                    access_token(),
                    user_id,
                    task_name_list,
                    task_priority_list,
                    end_date_list,
                )
            else:
                send_daily_remainder_no_task(access_token(), user_id)
            return
        if text_content.find("在岗人数") != -1 or text_content.find("number of on-duty") != -1:
            with open("attendance.txt", "r") as f:
                attendance_id_list = f.readlines()
            send_text_message(
                access_token(),
                target_id,
                "当前在岗人数：" + str(len(attendance_id_list)),
                message.get("chat_type"),
            )
            return
        if text_content.find("帮助") != -1 or text_content.find("help") != -1:
            content = {
                "zh_cn": {
                    "title": "PIP Bot 帮助",
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": "欢迎使用 PIP Bot！\nPIP Bot 是由",
                            },
                            {
                                "tag": "at",
                                "user_id": config["MANAGER_USER_ID"],
                            },
                            {
                                "tag": "text",
                                "text": "开发的。开源地址：",
                            },
                            {
                                "tag": "a",
                                "text": "PIP Bot Github 仓库",
                                "href": "https://github.com/gaohaojia/PIP_Bot",
                            },
                            {
                                "tag": "text",
                                "text": "。\n\n",
                            },
                        ],
                        [
                            {
                                "tag": "md",
                                "text": "**PIP Bot 目前支持以下功能：**\n",
                            },
                            {
                                "tag": "text",
                                "text": "1. 发送日报：在群里 @PIP Bot 或私聊 PIP Bot 并发送关键字“日报”或“daily report”，即可发送日报链接到群聊或私聊。\n",
                            },
                            {
                                "tag": "text",
                                "text": "2. 发送帮助：在群里 @PIP Bot 或私聊 PIP Bot 并发送关键字“帮助”或“help”，即可获取帮助信息。\n",
                            },
                            {
                                "tag": "text",
                                "text": "3. 发送任务：私聊 PIP Bot 并发送关键字“任务”或“task”，即可获取今日任务。\n",
                            },
                            {
                                "tag": "text",
                                "text": "4. 发送在岗人数：在群里 @PIP Bot 或私聊 PIP Bot 并发送关键字“在岗人数”或“number of on-duty”，即可获取当前在岗人数。\n",
                            },
                            {
                                "tag": "text",
                                "text": "其他功能正在开发中，敬请期待。",
                            },
                            {
                                "tag": "emotion",
                                "emoji_type": "SMART",
                            },
                        ],
                    ],
                },
            }
            send_post_message(
                access_token(), target_id, content, message.get("chat_type")
            )
            return
    send_text_message(
        access_token(),
        target_id,
        "PIP Bot 暂时还无法理解该内容，请给我学习的时间。\n回复“帮助”或“help”获取更多帮助。",
        message.get("chat_type"),
    )


def handle_advanced_permission_event(message):
    # 处理高级权限事件
    text_content: str = json.loads(message.get("content")).get("text")
    if text_content.find("下班提醒") != -1:
        user_id_list = update_user_id_list(access_token())
        for user_id in user_id_list:
            send_off_duty_reminder(access_token(), user_id)
        return True
    if text_content.find("打卡提醒") != -1:
        user_id_list = update_user_id_list(access_token())
        for user_id in user_id_list:
            send_daily_report_link(access_token(), user_id, "p2p")
        return True
    return False


def handle_bitable_event(event):
    # 处理bitable记录变更事件
    user_id = event.get("operator_id").get("open_id")
    action_list = event.get("action_list")
    for action in action_list:
        if action.get("action") == "record_added":
            pass


def handle_attendance_event(event):
    # 处理考勤事件
    with open("attendance.txt", "w+") as f:
        attendance_id_list = f.readlines()
        employee_id = event.get("employee_id")
        if employee_id not in attendance_id_list:
            attendance_id_list.append(employee_id)
            send_check_in_message(
                access_token(), convert_employee_id_to_user_id(employee_id)
            )
        else:
            attendance_id_list.remove(employee_id)
            send_check_out_message(
                access_token(), convert_employee_id_to_user_id(employee_id)
            )
        for id in attendance_id_list:
            f.write(id + "\n")


def start_flask():
    app.run(port=5000)


if __name__ == "__main__":
    start_flask()
