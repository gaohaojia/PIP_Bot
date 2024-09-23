import requests


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


if __name__ == "__main__":
    from access_token import AccessTokenClass
    from chat_id import get_chat_id

    access_token = AccessTokenClass().get_access_token()
    chat_id = get_chat_id(access_token, "战队大群")
    for user_id in get_users_id_from_chat(access_token, chat_id):
        print(user_id)
