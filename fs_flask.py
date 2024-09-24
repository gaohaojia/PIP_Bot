from flask import Flask, request, jsonify
import hashlib
import os
import json
import yaml

from fs_tasks import send_daily_report_link, send_text_message, send_post_message
from fs_id import AccessTokenClass

with open("FS_KEY.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

access_token = AccessTokenClass()

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

    if req_header.get("event_type") == "im.message.receive_v1":
        handle_message_event(req_data.get("event"))
        return jsonify({"success": True})

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
        text_content: str = json.loads(message.get("content")).get("text")
        if text_content.find("日报") != -1 or text_content.find("daily report") != -1:
            send_daily_report_link(access_token(), target_id, message.get("chat_type"))
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


def start_flask():
    app.run(port=5000)


if __name__ == "__main__":
    start_flask()
