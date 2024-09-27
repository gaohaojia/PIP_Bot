import requests
import yaml

with open("FS_KEY.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def get_chat_id(access_token, chat_name):
    url = "https://open.feishu.cn/open-apis/im/v1/chats"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"page_size": 100}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return None
    result = response.json()
    if result["code"] != 0:
        return None
    for chat in result["data"]["items"]:
        if chat["name"] == chat_name:
            return chat["chat_id"]
    return None


def get_users_id_from_chat(access_token, chat_id):
    url = "https://open.feishu.cn/open-apis/im/v1/chats/{}/members".format(chat_id)
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"page_size": 100}
    page_token = None
    while True:
        if page_token:
            params["page_token"] = page_token
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            break
        result = response.json()
        if result["code"] != 0:
            break
        for member in result["data"]["items"]:
            yield member["member_id"]
        if not result["data"]["has_more"]:
            break
        page_token = result["data"]["page_token"]


def update_user_id_list(access_token):
    chat_id = get_chat_id(access_token, config["CHAT_NAME"])
    if not chat_id:
        return []
    user_id_list = list(get_users_id_from_chat(access_token, chat_id))
    if len(user_id_list) == 0:
        return []
    return user_id_list

def convert_employee_id_to_user_id(access_token, employee_id):
    url = "https://open.feishu.cn/open-apis/contact/v3/users/{}".format(employee_id)
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"user_id_type": "user_id"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return None
    result = response.json()
    if result["code"] != 0:
        return None
    return result["data"]["user"]["open_id"]


if __name__ == "__main__":
    from access_token import AccessTokenClass

    access_token = AccessTokenClass()
    # chat_id = get_chat_id(access_token(), "战队大群")
    # for user_id in get_users_id_from_chat(access_token, chat_id):
    #     print(user_id)

    print(convert_employee_id_to_user_id(access_token(), "c8a58b89"))
