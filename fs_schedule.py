import time
import schedule
import yaml

from fs_id import AccessTokenClass, update_user_id_list
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
    get_tasks_by_user,
)

access_token = AccessTokenClass()


def daily_tasks_remainder():
    user_id_list = update_user_id_list()
    for user_id in user_id_list:
        task_name_list, task_priority_list, end_date_list = get_tasks_by_user(
            access_token(), user_id
        )
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
    user_id_list = update_user_id_list()
    for user_id in user_id_list:
        send_daily_report_link(access_token(), user_id)


def off_duty_reminder():
    user_id_list = update_user_id_list()
    for user_id in user_id_list:
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
