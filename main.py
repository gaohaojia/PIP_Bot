from fs_id import AccessTokenClass, get_chat_id, get_users_id_from_chat
from fs_tasks import (
    get_projects_items,
    get_tasks_items,
    get_daily_items,
    send_create_project_message,
    send_daily_remainder,
    send_daily_remainder_no_task
)
import time
import schedule

CHAT_NAME = "战队大群"

access_token_obj = AccessTokenClass()


def daily_tasks_remainder(user_id_list):
    access_token = access_token_obj.get_access_token()
    if not access_token:
        print("get access_token failed")
        return
    task_list = get_tasks_items(
        access_token, ["任务", "优先级", "状态", "开始时间", "截止时间", "任务执行人"]
    )
    for user_id in user_id_list:
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
                    if user["id"] == user_id:
                        task_name_list.append(task["fields"]["任务"][0]["text"])
                        task_priority_list.append(task["fields"]["优先级"])
                        end_date_list.append(task["fields"]["截止时间"])
            except:
                continue
        if len(task_name_list) > 0:
            send_daily_remainder(
                access_token, user_id, task_name_list, task_priority_list, end_date_list
            )
        else:
            send_daily_remainder_no_task(access_token, user_id)


if __name__ == "__main__":
    # get access_token
    access_token = access_token_obj.get_access_token()
    if not access_token:
        print("get access_token failed")
        exit()

    # get chat_id
    chat_id = get_chat_id(access_token, CHAT_NAME)
    if not chat_id:
        print("get chat_id failed")
        exit()

    # get users_id_from_chat
    user_id_list = list(get_users_id_from_chat(access_token, chat_id))
    if len(user_id_list) == 0:
        print("get users_id_from_chat failed")
        exit()

    daily_tasks_remainder(user_id_list)
    # send_daily_remainder(access_token, "ou_d11957b1eccd9e340b72fbc83c6eb41c", ["任务1", "任务2"], ["P0", "P1"], ["1727366400000", "1726329600000"])
    # send_create_project_message(access_token, "ou_d11957b1eccd9e340b72fbc83c6eb41c", "自动化测试项目", "自动化测试项目内容", "1727366400000", "ou_d11957b1eccd9e340b72fbc83c6eb41c", "进行中")

    # while True:
    #     schedule.every().day.at("00:00").do(daily_tasks_remainder)
