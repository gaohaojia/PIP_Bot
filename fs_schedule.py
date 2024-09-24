import time
import schedule
import yaml

from fs_id import AccessTokenClass, get_chat_id, get_users_id_from_chat
from fs_tasks import (
    get_projects_items,
    get_tasks_items,
    get_daily_items,
    send_create_project_message,
    send_daily_remainder,
    send_daily_remainder_no_task,
    send_text_message,
    send_daily_report_link,
    send_off_duty_reminder,
)

with open("FS_KEY.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

access_token = AccessTokenClass()

GLOBAL_USER_ID_LIST = []


def update_user_id_list():
    global GLOBAL_USER_ID_LIST
    chat_id = get_chat_id(access_token(), config["CHAT_NAME"])
    if not chat_id:
        send_text_message(access_token(), config["MANAGER_USER_ID"], "获取群聊ID失败")
        exit()
    user_id_list = list(get_users_id_from_chat(access_token(), chat_id))
    if len(user_id_list) == 0:
        send_text_message(access_token(), config["MANAGER_USER_ID"], "获取用户列表失败")
        return
    GLOBAL_USER_ID_LIST = user_id_list


def daily_tasks_remainder():
    task_list = get_tasks_items(
        access_token(), ["任务", "优先级", "状态", "开始时间", "截止时间", "任务执行人"]
    )
    update_user_id_list()
    for user_id in GLOBAL_USER_ID_LIST:
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
        if len(task_name_list) > 0:
            send_daily_remainder(
                access_token(),
                user_id,
                task_name_list,
                task_priority_list,
                end_date_list,
            )
        else:
            send_daily_remainder_no_task(access_token(), user_id)


def daily_report_remainder():
    update_user_id_list()
    for user_id in GLOBAL_USER_ID_LIST:
        send_daily_report_link(access_token(), user_id)


def off_duty_reminder():
    update_user_id_list()
    for user_id in GLOBAL_USER_ID_LIST:
        send_off_duty_reminder(access_token(), user_id)


def start_schedule():
    schedule.every().day.at("08:00").do(daily_tasks_remainder)
    schedule.every().day.at("21:00").do(daily_report_remainder)
    schedule.every().day.at("23:00").do(off_duty_reminder)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    start_schedule()
