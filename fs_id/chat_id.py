import requests


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


if __name__ == "__main__":
    from access_token import AccessTokenClass

    access_token = AccessTokenClass().get_access_token()
    chat_id = get_chat_id(access_token(), "战队大群")
    if chat_id:
        print(f"chat_id: {chat_id}")
    else:
        print("chat not found")
